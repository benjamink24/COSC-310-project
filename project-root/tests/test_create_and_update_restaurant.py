import json

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.api.routes import restaurant_endpoints
from app.repositories.restaurant_repo import resRepo

client = TestClient(app)

SEED = [
    {
        "id": 1,
        "Name": "Seed Restaurant",
        "Cuisine": "Any",
        "Address": "1 Seed St",
        "Hours": "9:00 AM - 5:00 PM",
        "Photos": [],
        "menu": [],
    }
]


@pytest.fixture(autouse=True)
def temp_data(tmp_path, monkeypatch):
    """Point the app at a fresh temp file for every test. test.json is never touched."""
    data_file = tmp_path / "data.json"
    data_file.write_text(json.dumps(SEED))
    monkeypatch.setattr(restaurant_endpoints.restaurant.repo, "file_path", data_file)
    return data_file


def _find_id(data_file, name):
    matches = [r for r in resRepo(str(data_file)).get_all_restaurants() if r["Name"] == name]
    return matches[-1]["id"]


def test_create_and_update_restaurant(temp_data):
    new_res = {
        "Name": "Test Bistro",
        "Cuisine": "Fusion",
        "Address": "123 Test St",
        "Hours": "9:00 AM - 5:00 PM",
        "Photos": [],
        "menu": [],
    }
    response = client.post("/restaurants", json=new_res)
    assert response.status_code == 201
    assert response.json()["Name"] == "Test Bistro"
    new_id = _find_id(temp_data, "Test Bistro")

    update_data = {**new_res, "Name": "Test Bistro Updated", "Cuisine": "Modern Fusion"}
    response = client.put(f"/restaurants/{new_id}", json=update_data)
    assert response.status_code == 201
    assert response.json()["Name"] == "Test Bistro Updated"