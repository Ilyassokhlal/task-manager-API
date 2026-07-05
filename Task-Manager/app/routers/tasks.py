
from fastapi import APIRouter, Depends, Query, BackgroundTasks, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional
from app.database import get_db
from app.models.task import Task
from app.models.user import User
from app.schemas.task import SuggestionResponse, TaskCreate, TaskPriority, TaskUpdate, TaskPatch, TaskResponse
from app.utils.exceptions import NotFoundException, DuplicateException, BadRequestException, ForbiddenException
from app.utils.security import get_current_user
from app.utils.notifications import log_activity, send_notification
from app.utils.limiter import limiter
from datetime import datetime

router = APIRouter(prefix="/tasks", tags= ["Tasks"])

def get_task_or_404(db: Session, task_id: int) -> Task:
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise NotFoundException("Task", task_id)
    return task

@router.post("/", response_model=TaskResponse, status_code=201,
    responses={
        422: {"description": "Validation Error"},
        401: {"description": "Not authenticated"},
        400: {"description": "Task already exists"},
        429: {"description": "Too many requests"},
    },
    summary="Add a new task.",
)
@limiter.limit("20/minute")
def add_task(request: Request, task: TaskCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Add a new task to the database.
    
    - Each user can have many tasks.
    - The task record is associated with the currently authenticated user.
    - Returns the created task with its data.
    """
    existing_task = db.query(Task).filter(Task.user_id == current_user.id, Task.title == task.title).first()
    if existing_task:
        raise BadRequestException("This user already has a task with the same title. Only one task per title per user allowed.")

    db_task = Task(**task.model_dump(), user_id=current_user.id)
    try:
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
    except IntegrityError:
        db.rollback()
        raise DuplicateException("Task", "title", task.title)
    
    background_tasks.add_task(send_notification, email=current_user.email, message=f"Hi {current_user.username}. You have successfully added a new task!")
    print(f"Background task added | Send a confirmation email to {current_user.email}")

    background_tasks.add_task(log_activity, user_id=current_user.id, action="Task added")
    print(f"Background task added | Log activity for user_id {current_user.id}")

    return db_task

@router.get("/", response_model=list[TaskResponse],
    responses={
        429: {"description": "Too many requests"},
    },
    summary="List all tasks",
)
@limiter.limit("60/minute")
def list_tasks(
    request: Request,
    due_date: Optional[datetime] = Query(default=None, description="Filter tasks by due date (YYYY-MM-DD)"),
    completed: Optional[bool] = Query(default=None, description="Filter tasks by completion status (True or False)"),
    priority: Optional[TaskPriority] = Query(default=None, description="Filter tasks by priority"),
    skip: int = Query(default=0, ge=0, description="Number of tasks to skip."),
    limit: int = Query(default=5, ge=1, le=100, description="Maximum number of tasks to return."),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all tasks in the database, with optional filtering.
    
    - due_date: Filter tasks by their due date (YYYY-MM-DD).
    - completed: Filter tasks by their completion status (e.g., True, False).
    - priority: Filter tasks by their priority (e.g., high, medium, low).
    - Returns a list of tasks matching the specified filters.
    - If no filters are provided, all tasks will be returned.
    - Raises a 429 error if the request rate limit is exceeded.
    """
    query = db.query(Task).filter(Task.user_id == current_user.id)

    if due_date is not None:
        query = query.filter(Task.due_date == due_date)
    if completed is not None:
        query = query.filter(Task.completed == completed)
    if priority is not None:
        query = query.filter(Task.priority == priority)

    return query.all()

@router.get("/{task_id}", response_model=TaskResponse,
    responses={
        404: {"description": "Task not found"},
        429: {"description": "Too many requests"},
    },
    summary="Get a specific task by ID",
)
@limiter.limit("60/minute")
def get_task(request: Request, task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Retrieve a specific task by its ID.
    - Returns the task data if found.
    - Raises a 404 error if the task does not exist.
    """
    db_task = get_task_or_404(db, task_id)
    
    if db_task.user_id != current_user.id:
        raise ForbiddenException()

    return db_task

@router.put("/{task_id}", response_model=TaskResponse,
    responses={
        400: {"description": "Bad Request"},
        401: {"description": "Not authenticated"},
        403: {"description": "Forbidden"},
        404: {"description": "Task not found"},
        429: {"description": "Too many requests"},
    },
    summary="Update a specific task by ID",
)
@limiter.limit("20/minute")
def update_task(request: Request, task_id: int, data: TaskUpdate, background_tasks: BackgroundTasks, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Fully update a specific task by its ID.

    - All fields must be provided.
    - Raises a 400 error if the task is completed and an attempt is made to uncomplete.
    - Returns the updated task data.
    """
    
    db_task = get_task_or_404(db, task_id)

    if db_task.user_id != current_user.id:
        raise ForbiddenException()

    if db_task.completed == True and data.completed == False:
        raise BadRequestException("Completed tasks cannot be uncompleted")

    for field, value in data.model_dump().items():
        setattr(db_task, field, value)
    db.commit()
    db.refresh(db_task)

    background_tasks.add_task(send_notification, email=current_user.email, message=f"Hi {current_user.username}. Your task information has been fully updated!")
    print(f"Background task added | Send a confirmation email to {current_user.email}")

    background_tasks.add_task(log_activity, user_id=current_user.id, action="Task fully updated")
    print(f"Background task added | Log activity for user_id {current_user.id}")

    return db_task

@router.patch("/{task_id}", response_model=TaskResponse,
    responses={
        400: {"description": "Bad Request"},
        401: {"description": "Not authenticated"},
        403: {"description": "Forbidden"},
        404: {"description": "Task not found"},
        429: {"description": "Too many requests"},
    },
    summary="Partially update a specific task by ID",
)
@limiter.limit("20/minute")
def patch_task(request: Request, task_id: int, data: TaskPatch, background_tasks: BackgroundTasks, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Partially update a specific task by its ID.

    - Only the fields provided in the request will be updated.
    - Raises a 400 error if the task is completed and an attempt is made to uncomplete.
    - Returns the updated task data.
    """

    db_task = get_task_or_404(db, task_id)

    if db_task.user_id != current_user.id:
        raise ForbiddenException()

    if db_task.completed == True and data.completed == False:
        raise BadRequestException("Completed tasks cannot be uncompleted")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(db_task, field, value)
    db.commit()
    db.refresh(db_task)
    
    background_tasks.add_task(send_notification, email=current_user.email, message=f"Hi {current_user.username}. Your task information has been partially updated!")

    print(f"Background task added | Send a confirmation email to {current_user.email}")
    
    background_tasks.add_task(log_activity, user_id=current_user.id, action="Task partially updated")
    print(f"Background task added | Log activity for user_id {current_user.id}")
    
    return db_task

@router.delete("/{task_id}", status_code=204,
    responses={
        400: {"description": "Bad Request"},
        401: {"description": "Not authenticated"},
        403: {"description": "Forbidden"},
        404: {"description": "Task not found"},
        429: {"description": "Too many requests"},
    },
    summary="Delete a specific task by ID",
)
@limiter.limit("20/minute")
def delete_task(request: Request, task_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Delete a specific task by its ID.

    - Only tasks that are currently completed can be deleted.
    - Raises a 400 error if an attempt is made to delete a pending or in-progress task.
    - Returns a 204 status code upon successful deletion.
    """
    db_task = get_task_or_404(db, task_id)
    if db_task.user_id != current_user.id:
        raise ForbiddenException()
    if not db_task.completed:
        raise BadRequestException("Only completed tasks can be deleted")
    db.delete(db_task)
    db.commit()

    background_tasks.add_task(log_activity, user_id=current_user.id, action="Task deleted")
    print(f"Background task added | Log activity for user_id {current_user.id}")


@router.post("/{task_id}/suggest", response_model=SuggestionResponse,
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Forbidden"},
        404: {"description": "Task not found"},
        429: {"description": "Too many requests"},
    },
    summary="Get a suggestion for a specific task by ID",
)
@limiter.limit("10/minute")
def suggest_task(request: Request, task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Get a suggestion for a specific task by its ID.

    - This endpoint provides suggestions based on the task's title and description.
    - Raises a 404 error if the task does not exist.
    - Returns a suggestion string related to the task.
    """
    db_task = get_task_or_404(db, task_id)

    if db_task.user_id != current_user.id:
        raise ForbiddenException()

    # Placeholder Response
    suggestion = f"Consider breaking down the task '{db_task.title}' into smaller tasks to manage them better."

    return SuggestionResponse(task_id=task_id, suggestion=suggestion)