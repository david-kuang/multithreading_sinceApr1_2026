
from app.main import app
from fastapi.testclient import TestClient
client=TestClient(app)

def test_validation():
    r=client.post('/chat',json={})
    assert r.status_code==422
