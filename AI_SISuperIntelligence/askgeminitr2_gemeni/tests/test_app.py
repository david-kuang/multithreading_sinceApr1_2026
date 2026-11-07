def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome" in response.json()["message"]


def test_user_registration(client):
    response = client.post(
        "/api/auth/register",
        json={"username": "geminiuser", "password": "securepassword123"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "geminiuser"
    assert "id" in data


def test_user_login(client):
    client.post(
        "/api/auth/register",
        json={"username": "geminiuser", "password": "securepassword123"}
    )
    response = client.post(
        "/api/auth/token",
        data={"username": "geminiuser", "password": "securepassword123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_ask_gemini_workflow(client):
    """Integration test verifying full lifecycle: Register -> Create Session -> Submit Query -> Get Details."""
    # 1. Register User
    client.post(
        "/api/auth/register",
        json={"username": "testqa", "password": "password123"}
    )

    # 2. Create Search Session
    session_res = client.post(
        "/api/sessions",
        json={"title": "Python FastAPI Exploration"}
    )
    assert session_res.status_code == 201
    session_data = session_res.json()
    session_id = session_data["id"]
    assert session_data["title"] == "Python FastAPI Exploration"

    # 3. Submit Query to Gemini
    query_res = client.post(
        f"/api/sessions/{session_id}/queries",
        json={"prompt": "Explain dependency injection in FastAPI."}
    )
    assert query_res.status_code == 201
    query_data = query_res.json()
    assert "Gemini AI Response" in query_data["response"]

    # 4. Retrieve Session Details & History
    detail_res = client.get(f"/api/sessions/{session_id}")
    assert detail_res.status_code == 200
    detail_data = detail_res.json()
    assert len(detail_data["queries"]) == 1
    assert detail_data["queries"][0]["prompt"] == "Explain dependency injection in FastAPI."