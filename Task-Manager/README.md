# Task Manager API

A FastAPI-based task management API with JWT authentication, task CRUD,
and a placeholder AI suggestion endpoint.

## Features
- User registration & login with JWT authentication
- Password hashing with bcrypt
- Task CRUD (create, list, get, patch, delete), scoped to the authenticated user
- Filtering (completed, priority) and pagination on task listing
- Rate limiting on all endpoints
- Background tasks for notifications and activity logging
- Auto-generated Swagger docs at `/docs`

## Tech Stack
- FastAPI
- SQLAlchemy (SQLite)
- Pydantic v2
- JWT (python-jose)
- bcrypt (passlib)
- slowapi (rate limiting)
- pytest

## Setup

### 1. Clone the repo and navigate into it

**Windows:**
```
cd task-manager
```

**Bash:**
```bash
cd task-manager
```

### 2. Create a virtual environment and activate it

**Windows:**
```
python -m venv venv
venv\Scripts\activate
```

**Bash:**
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

**Windows:**
```
pip install -r requirements.txt
```

**Bash:**
```bash
pip install -r requirements.txt
```

### 4. Create a `.env` file in the project root

**Windows:**
```
echo SECRET_KEY=your-secret-key-here > .env
echo DEBUG=True >> .env
```

**Bash:**
```bash
echo "SECRET_KEY=your-secret-key-here" > .env
echo "DEBUG=True" >> .env
```

### 5. Run the app

**Windows:**
```
uvicorn app.main:app --reload
```

**Bash:**
```bash
uvicorn app.main:app --reload
```

### 6. Open Swagger docs
http://localhost:8000/docs

## Running Tests

**Windows:**
```
pytest
```

**Bash:**
```bash
pytest
```

## API Overview

| Method | Endpoint | Description | Auth |
|--------|----------|--------------|------|
| POST | /auth/register | Register a new user | No |
| POST | /auth/login | Login and get a JWT | No |
| GET | /users/me | Get current user's profile | Yes |
| POST | /tasks | Create a task | Yes |
| GET | /tasks | List your tasks (filters + pagination) | Yes |
| GET | /tasks/{id} | Get a specific task | Yes |
| PATCH | /tasks/{id} | Partially update a task | Yes |
| PUT | /tasks/{id} | Fully update a task | Yes |
| DELETE | /tasks/{id} | Delete a task (must be completed) | Yes |
| POST | /tasks/{id}/suggest | Get a placeholder AI suggestion | Yes |

## Notes
- Completed tasks cannot be marked incomplete.
- Only completed tasks can be deleted.
- No two tasks can share the same name