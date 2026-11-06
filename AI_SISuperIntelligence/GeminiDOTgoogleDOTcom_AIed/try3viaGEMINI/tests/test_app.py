"""
Comprehensive PyTest unit and integration test suite for the AskGemini application.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.models import User

# In-memory SQLite database setup for unit testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Provides an isolated database session for testing."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Resets database state before and after each test."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_user_registration():
    """Tests successful user registration API endpoint."""
    response = client.post("/api/auth/register", json={"username": "geminiuser", "password": "securepassword123"})
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "geminiuser"
    assert "id" in data


def test_user_login():
    """Tests successful user authentication and token generation."""
    client.post("/api/auth/register", json={"username": "geminiuser", "password": "securepassword123"})
    response = client.post("/api/auth/token", data={"username": "geminiuser", "password": "securepassword123"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_ask_gemini_workflow():
    """
    Integration test verifying complete user lifecycle:
    Register -> Login -> Create Search Session -> Submit Query -> Retrieve Session Details.
    """
    # 1. Register and Login
    client.post("/api/auth/register", json={"username": "testqa", "password": "password123"})
    token_res = client.post("/api/auth/token", data={"username": "testqa", "password": "password123"})
    token = token_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create Search Session
    session_res = client.post("/api/sessions", headers=headers)
    assert session_res.status_code == 201
    session_id = session_res.json()["id"]

    # 3. Submit Query
    query_res = client.post(
        f"/api/sessions/{session_id}/queries",
        headers=headers,
        json={"prompt": "Explain quantum computing in simple terms"}
    )
    assert query_res.status_code == 200
    query_data = query_res.json()
    assert "response" in query_data

    # 4. Fetch Session History
    detail_res = client.get(f"/api/sessions/{session_id}", headers=headers)
    assert detail_res.status_code == 200
    queries = detail_res.json()["queries"]
    assert len(queries) == 1
    assert queries[0]["prompt"] == "Explain quantum computing in simple terms"

    # 5. Delete Session
    del_res = client.delete(f"/api/sessions/{session_id}", headers=headers)
    assert del_res.status_code == 204