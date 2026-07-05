import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

from app.utils.limiter import limiter

limiter.enabled = False

TEST_DATABASE_URL = "sqlite:///./tests/db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def auth_headers(client):
    client.post("/auth/register", json={
        "username": "testusername",
        "email": "testemail@student.com",
        "password": "testpassword123"
    })
    response = client.post("/auth/login", json={
        "email": "testemail@student.com",
        "password": "testpassword123"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def sample_task(client, auth_headers):
    """Create and return a sample task for tests that need existing data"""
    response = client.post("/tasks", json={
        "title": "Test Task",
        "description": "Test description",
        "due_date": "2024-12-31T23:59:59",
        "completed": False
    }, headers=auth_headers)

    return response.json()
