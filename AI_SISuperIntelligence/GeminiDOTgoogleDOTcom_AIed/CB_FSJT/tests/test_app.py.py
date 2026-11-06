"""
Comprehensive PyTest Integration & Unit Test Suite for ChatGPT Application.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.auth import get_password_hash
from app.models import User

# Configure isolated test database in memory
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Provides a fresh database session per test execution."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    """Fixtures for creating clean test database state per test case."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_register_user_success():
    """Tests successful user registration endpoint."""
    response = client.post("/api/auth/register", json={"username": "testuser", "password": "password123"})
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert "id" in data


def test_register_duplicate_username_fails():
    """Tests that registering duplicate usernames raises HTTP 400 error."""
    client.post("/api/auth/register", json={"username": "testuser", "password": "password123"})
    response = client.post("/api/auth/register", json={"username": "testuser", "password": "password123"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already registered"


def test_login_success():
    """Tests successful user login and access token retrieval."""
    client.post("/api/auth/register", json={"username": "testuser", "password": "password123"})
    response = client.post("/api/auth/token", data={"username": "testuser", "password": "password123"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_chat_workflow():
    """
    Integration test for end-to-end user chat workflow:
    Register -> Login -> Create Conversation -> Post Message -> Validate Response.
    """
    # 1. Register & Login
    client.post("/api/auth/register", json={"username": "chatuser", "password": "password123"})
    auth_res = client.post("/api/auth/token", data={"username": "chatuser", "password": "password123"})
    token = auth_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create conversation
    conv_res = client.post("/api/conversations", headers=headers)
    assert conv_res.status_code == 201
    conv_id = conv_res.json()["id"]

    # 3. Send message
    msg_res = client.post(
        f"/api/conversations/{conv_id}/messages",
        headers=headers,
        json={"content": "Hello AI!"}
    )
    assert msg_res.status_code == 200
    msg_data = msg_res.json()
    assert msg_data["role"] == "assistant"
    assert "[Simulated Response]" in msg_data["content"]

    # 4. Get conversation history details
    details_res = client.get(f"/api/conversations/{conv_id}", headers=headers)
    assert details_res.status_code == 200
    messages = details_res.json()["messages"]
    assert len(messages) == 2
    assert messages[0]["content"] == "Hello AI!"
    assert messages[0]["role"] == "user"

    # 5. Delete conversation
    del_res = client.delete(f"/api/conversations/{conv_id}", headers=headers)
    assert del_res.status_code == 204