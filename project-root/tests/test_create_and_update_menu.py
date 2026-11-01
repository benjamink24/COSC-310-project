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


def test_menu_operations(temp_data):
    res = client.post("/restaurants", json={
        "Name": "Menu Test Place",
        "Cuisine": "Any",
        "Address": "1 Test St",
        "Hours": "9:00 AM - 5:00 PM",
        "Photos": [],
        "menu": [],
    })
    assert res.status_code == 201
    rid = _find_id(temp_data, "Menu Test Place")

    menu_item = {"Name": "Truffle Fries", "Price": 10.50, "Availability": True}
    response = client.post(f"/restaurants/{rid}/menu", json=menu_item)
    assert response.status_code == 201

    added = next((i for i in response.json()["menu"] if i["Name"] == "Truffle Fries"), None)
    assert added is not None
    assert added["Price"] == 10.50

    updated = {"Name": "Truffle Fries", "Price": 12.00, "Availability": False}
    response = client.put(f"/restaurants/{rid}/menu/Truffle Fries", json=updated)
    assert response.status_code == 200

    modified = next((i for i in response.json()["menu"] if i["Name"] == "Truffle Fries"), None)
    assert modified["Price"] == 12.00
    assert modified["Availability"] is False