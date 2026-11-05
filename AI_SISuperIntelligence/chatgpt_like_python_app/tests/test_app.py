"""Unit tests for the Flask chat application."""

import os
import pytest

os.environ.setdefault("FLASK_SECRET_KEY", "test-secret-key")

from app import create_app, db, Conversation, Message


@pytest.fixture()
def app(tmp_path):
    """Create an isolated test app and temporary SQLite database."""
    database = "sqlite:///" + str(tmp_path / "test.sqlite").replace("\\", "/")
    application = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret",
        "SQLALCHEMY_DATABASE_URI": database,
        "WTF_CSRF_ENABLED": False,
    })
    with application.app_context():
        db.drop_all()
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    """Return a Flask test client."""
    return app.test_client()


def get_csrf(client):
    """Read a CSRF token from the rendered home page's session cookie."""
    response = client.get("/")
    assert response.status_code == 200
    with client.session_transaction() as sess:
        return sess["_csrf_token"]


def test_home_page_loads(client):
    """The home page should render successfully."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"AI Chat" in response.data


def test_csrf_rejects_missing_token(client):
    """State-changing requests without CSRF protection should fail."""
    response = client.post("/conversations")
    assert response.status_code == 400


def test_create_and_delete_conversation(client, app):
    """A user can create and delete a conversation."""
    token = get_csrf(client)
    response = client.post("/conversations", data={"csrf_token": token})
    assert response.status_code == 302
    with app.app_context():
        conversation = Conversation.query.one()
        conversation_id = conversation.id
    response = client.post(
        f"/conversations/{conversation_id}/delete",
        data={"csrf_token": token},
    )
    assert response.status_code == 302
    with app.app_context():
        assert Conversation.query.count() == 0


def test_chat_rejects_invalid_json(client):
    """The chat endpoint validates the JSON request body."""
    token = get_csrf(client)
    response = client.post(
        "/api/chat",
        data="not-json",
        content_type="application/json",
        headers={"X-CSRF-Token": token},
    )
    assert response.status_code == 400


def test_chat_rejects_empty_message(client):
    """The chat endpoint rejects blank prompts."""
    token = get_csrf(client)
    response = client.post(
        "/api/chat",
        json={"message": "   "},
        headers={"X-CSRF-Token": token},
    )
    assert response.status_code == 400


def test_conversation_not_found(client):
    """Unknown conversation IDs return 404."""
    response = client.get("/api/conversations/9999")
    assert response.status_code == 404


def test_conversation_api_returns_messages(client, app):
    """Conversation API returns persisted messages."""
    with app.app_context():
        conversation = Conversation(title="Test")
        db.session.add(conversation)
        db.session.flush()
        db.session.add(Message(
            conversation_id=conversation.id, role="user", content="Hi"
        ))
        db.session.commit()
        conversation_id = conversation.id

    response = client.get(f"/api/conversations/{conversation_id}")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["messages"][0]["content"] == "Hi"
    assert payload["messages"][0]["role"] == "user"
