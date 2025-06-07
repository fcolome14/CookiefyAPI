import pytest
from app.schemas.post import ListCreate

def test_create_list_success(client):
    payload = {
        "name": "My List",
        "description": "this is a test list",
        "accepts_contributions": False,
        "is_public": True
    }
    response = client.post("/posts/create-list", json=payload)
    assert response.status_code == 201
    assert response.json()["message"] == "List created successfully."

def test_create_list_duplicate(client):
    payload = {
        "name": "Duplicate List",
        "description": "desc",
        "accepts_contributions": False,
        "is_public": True
    }
    # First insert
    _ = client.post("/posts/create-list", json=payload)
    # Duplicate insert
    response2 = client.post("/posts/create-list", json=payload)
    
    assert response2.status_code == 201
    assert "already exists" in response2.json()["message"]
