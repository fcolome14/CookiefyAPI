from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_user():
    response = client.post("/api/users/", json={"name": "John Doe", "email": "john@example.com", "password": "secret123"})
    assert response.status_code == 200
    assert response.json()["email"] == "john@example.com"
