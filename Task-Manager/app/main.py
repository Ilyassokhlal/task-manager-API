"""
Security measures in place:
    - CORS: restricted to localhost 8501 & 3000 | Methods are also limited to "POST" & "GET", "PUT", "DELETE" and "PATCH" as they are needed for the task management API.
    - Rate Limiting:
            login: 5 requests per minute
            all POST, PUT, DELETE, PATCH requests: 20 requests per minute
            all GET requests: 60 requests per minute
    - Input Validation (pydantic does this):
        user fields:
            username: (36 max characters)
            password: (8 min & 72 max characters)
            email: validated with EmailStr
        task fields:
            title: (200 max characters)
            description: (2000 max characters)
            due_date: (ISO 8601 date format)
            completed: (boolean)
"""


from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.database import engine, Base
from app.routers import auth, tasks
from app.utils.exceptions import AppException
from app.routers import users
from app.utils.limiter import limiter

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

tags_metadata = [
    {"name": "Authentication", "description": "User registration and login. All protected endpoints require a Bearer token."},
    {"name": "Tasks", "description": "CRUD operations for task records. Most endpoints require authentication."},
    {"name": "Users", "description": "Get the current user's profile information. Requires authentication."}
]


app = FastAPI(
    title= "Task Management API",
    description= """This API allows you to manage task records, including creating, reading, updating, and deleting task information. It also includes user authentication and registration.

    ## Quick Start
    1. Register a new user using the `/auth/register` endpoint.
    2. Log in using the `/auth/login` endpoint to receive a JWT access token.
    3. Use the access token to authenticate requests to protected endpoints for managing task records.
    4. Start by adding a task using the `/tasks/` endpoint.
    """,
    version= "1.0.0",
    openapi_tags=tags_metadata,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["POST", "GET", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"]    
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(users.router)

@app.get("/")
def root():
    return {"message": "Task Management API is running. Visit /docs for API documentation."}

@app.exception_handler(AppException)
def handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )