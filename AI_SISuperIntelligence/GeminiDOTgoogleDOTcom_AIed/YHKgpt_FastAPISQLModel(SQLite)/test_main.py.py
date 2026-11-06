"""
Comprehensive unit and integration test suite using pytest and FastAPI TestClient.
Tests application routes, database persistence, and error handling.
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine
from sqlmodel.pool import StaticPool

# Setup test database before importing main app
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

import database
import main

# Override engine in database module for testing
database.engine = test_engine

@pytest.fixture(autouse=True)
def setup_database():
    """Creates and drops database tables for each test."""
    SQLModel.metadata.create_all(test_engine)
    yield
    SQLModel.metadata.drop_all(test_engine)

@pytest.fixture
def client():
    """Provides a TestClient instance for FastAPI application testing."""
    return TestClient(main.app)

def test_read_root(client):
    """Test that the root endpoint serves the frontend HTML file."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_create_conversation(client):
    """Test creating a new conversation."""
    response = client.post("/api/conversations")
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["title"] == "New Chat"

def test_list_conversations(client):
    """Test listing conversations."""
    client.post("/api/conversations")
    response = client.get("/api/conversations")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

def test_send_and_get_messages(client):
    """Test sending a message and retrieving conversation history."""
    conv_res = client.post("/api/conversations")
    conv_id = conv_res.json()["id"]

    msg_payload = {"content": "Hello, AI!"}
    msg_res = client.post(f"/api/conversations/{conv_id}/messages", json=msg_payload)
    assert msg_res.status_code == 201
    msg_data = msg_res.json()
    assert msg_data["role"] == "assistant"
    assert "Echo response" in msg_data["content"]

    get_res = client.get(f"/api/conversations/{conv_id}/messages")
    assert get_res.status_code == 200
    messages = get_res.json()
    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "Hello, AI!"
    assert messages[1]["role"] == "assistant"

def test_conversation_not_found(client):
    """Test error handling when accessing a non-existent conversation."""
    response = client.get("/api/conversations/999/messages")
    assert response.status_code == 404
    assert response.json()["detail"] == "Conversation not found."

    post_response = client.post("/api/conversations/999/messages", json={"content": "Test"})
    assert post_response.status_code == 404
    assert post_response.json()["detail"] == "Conversation not found."