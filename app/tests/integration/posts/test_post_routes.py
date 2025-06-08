import pytest

@pytest.fixture
def list_payload():
    return {
        "name": "Test Add List",
        "description": "This is a test list",
        "accepts_contributions": False,
        "is_public": True
    }


def test_create_list_success(client, list_payload):
    response = client.post("/posts/create-list", json=list_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "List created successfully."
    assert "id" in data["data"]
    assert "meta" in data


def test_create_list_duplicate(client):
    payload = {
        "name": "Test Duplicate List",
        "description": "This is a duplicate list",
        "accepts_contributions": True,
        "is_public": False
    }

    res1 = client.post("/posts/create-list", json=payload)
    assert res1.status_code == 201
    res2 = client.post("/posts/create-list", json=payload)
    assert res2.status_code == 201
    data = res2.json()
    assert "already exists" in data["message"].lower()
    assert "meta" in data


def test_get_list_success(client):
    response = client.get("/posts/get-list")
    assert response.status_code == 200
    data = response.json()
    assert "lists" in data["data"]
    assert isinstance(data["data"]["lists"], list)
    assert "meta" in data


def test_update_list_success(client):
    update_payload = {
        "id": 1,
        "name": "Updated List Name",
        "sites": [1,2],
        "description": "Updated description"
    }
    response = client.put("/posts/update-list", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "List updated successfully."
    assert data["data"]["name"] == "Updated List Name"
    assert "meta" in data


def test_update_list_not_found(client):
    payload = {
        "id": 9999,
        "name": "Nonexistent"
    }
    response = client.put("/posts/update-list", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "not found" in data["message"].lower()


def test_delete_list_success(client):
    delete_payload = {"id": [2]}
    response = client.request("DELETE", "/posts/delete-list", json=delete_payload)
    assert response.status_code == 200
    data = response.json()
    assert "deleted successfully" in data["message"].lower()
    assert "meta" in data


def test_delete_list_not_found(client):
    payload = {"id": [99999]}
    response = client.request("DELETE", "/posts/delete-list", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "not found" in data["message"].lower()
