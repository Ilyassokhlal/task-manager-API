from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class TaskPriority(str, Enum):
    """Enum for task priority"""
    low = "low"
    medium = "medium"
    high = "high"

class TaskCreate(BaseModel):
    """Schema for adding a new task"""
    title: str = Field(
        min_length=1, max_length=200,
        description="The title of the task.",
        examples=["Complete project"]
    )
    description: Optional[str] = Field(
        default=None, max_length=2000,
        description="A brief description of the task.",
        examples=["Finish the initial design"]
    )
    due_date: Optional[datetime] = Field(
        default=None,
        description="The due date of the task.",
        examples=["2023-12-31"]
    )
    completed: bool = Field(
        default=False,
        description="The completion status of the task.",
        examples=[False]
    )
    priority: TaskPriority = Field(
        default=TaskPriority.medium,
        description="The priority of the task.",
        examples=["high"]
        )

class TaskUpdate(BaseModel):
    """Schema for fully updating a task"""
    title: str = Field(
        min_length=1, max_length=200,
        description="The title of the task.",
        examples=["Complete project"]
    )
    description: Optional[str] = Field(
        default=None, max_length=2000,
        description="A brief description of the task.",
        examples=["Finish the initial design"]
    )
    due_date: Optional[datetime] = Field(
        default=None,
        description="The due date of the task.",
        examples=["2023-12-31"]
    )
    completed: bool = Field(
        description="The completion status of the task.",
        examples=[False]
    )
    priority: TaskPriority = Field(
        description="The priority of the task.",
        examples=["high"]
    )

class TaskPatch(BaseModel):
    """Schema for partially updating a task"""
    title: Optional[str] = Field(
        default=None, max_length=200,
        description="The title of the task.",
        examples=["Complete project"]
    )
    description: Optional[str] = Field(
        default=None, max_length=2000,
        description="A brief description of the task.",
        examples=["Finish the initial design"]
    )
    due_date: Optional[datetime] = Field(
        default=None,
        description="The due date of the task.",
        examples=["2023-12-31"]
    )
    completed: Optional[bool] = Field(
        default=None,
        description="The completion status of the task.",
        examples=[False]
    )
    priority: Optional[TaskPriority] = Field(
        default=None,
        description="The priority of the task.",
        examples=["high"]
    )

class TaskResponse(BaseModel):
    """Schema for returning a task"""
    id: int
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    completed: bool
    priority: TaskPriority
    created_at: datetime
    updated_at: datetime
    user_id: int

    model_config = ConfigDict(
        from_attributes = True,
        json_schema_extra = {
            "example": {
                "id": 1, "title": "Complete project", "description": "Finish the initial design", "due_date": "2023-12-31", "completed": False, "priority": "high", "created_at": "2023-01-01T00:00:00", "updated_at": "2023-01-01T00:00:00", "user_id": 1
            }
        }
    )

class SuggestionResponse(BaseModel):
    """Schema for returning a suggestion"""
    task_id: int
    suggestion: str

    model_config = ConfigDict(
        from_attributes = True,
        json_schema_extra = {
            "example": {
                "task_id": 1,
                "suggestion": "Consider breaking down the task 'Complete project' into smaller tasks to manage them better."
            }
        }
    )
