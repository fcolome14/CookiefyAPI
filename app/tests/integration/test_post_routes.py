import pytest
from app.schemas.post import ListCreate

@pytest.mark.asyncio
async def test_create_list_success(async_client):
    payload = {
        "name": "My List",
        "description": "desc",
        "accepts_contributions": False,
        "is_public": True
    }
    response = await async_client.post("/posts/create-list", json=payload)
    assert response.status_code == 201
    assert response.json()["message"] == "List created successfully."

@pytest.mark.asyncio
async def test_create_list_duplicate(async_client):
    payload = {
        "name": "Duplicate List",
        "description": "desc",
        "accepts_contributions": False,
        "is_public": True
    }
    await async_client.post("/posts/create-list", json=payload)
    response = await async_client.post("/posts/create-list", json=payload)
    assert response.status_code == 200
    assert "already exists" in response.json()["message"]
