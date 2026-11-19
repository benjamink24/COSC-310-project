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
                    "Name": "Waterfront Wines",
                    "Cuisine": "Farm-to-Table",
                    "Address": "1180 Sunset Dr #104, Kelowna, BC",
                    "Hours": "5:00 PM - 10:00 PM",
                    "Photos": [],
                    "menu": [
                        {"Name": "Grilled Salmon", "Price": 32.0, "Availability": True},
                        {"Name": "Duck Confit", "Price": 36.0, "Availability": False},
                    ]
                }
]


@pytest.fixture(autouse=True)
def temp_data(tmp_path, monkeypatch):
    """Point the app at a fresh temp file for every test. test.json is never touched."""
    data_file = tmp_path / "data.json"
    data_file.write_text(json.dumps(SEED))
    monkeypatch.setattr(restaurant_endpoints.restaurant.repo, "file_path", data_file)
    return data_file


# --- Restaurant details ---


def test_get_valid_restaurant():
    response = client.get("/restaurants/1")
    assert response.status_code == 200
    assert response.json() == {
        "Name": "Waterfront Wines",
        "Cuisine": "Farm-to-Table",
        "Address": "1180 Sunset Dr #104, Kelowna, BC",
        "Hours": "5:00 PM - 10:00 PM"
    }


def test_restaurant_name_is_case_insensitive():
    assert client.get("/restaurants/1").status_code == 200


def test_get_invalid_restaurant():
    response = client.get("/restaurants/-1")
    assert response.status_code == 404
    assert response.json()["detail"] == "Restaurant not found"


# --- Menu ---


def test_get_valid_menu():
    response = client.get("/restaurants/1/menu")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    assert body[0] == {"Name": "Grilled Salmon", "Price": 32.0, "Availability": True}


def test_get_menu_invalid_restaurant():
    assert client.get("/restaurants/-1/menu").status_code == 404


# --- Menu item ---


def test_get_valid_menu_item():
    response = client.get("/restaurants/1/menu/Grilled Salmon")
    assert response.status_code == 200
    assert response.json() == {
        "Name": "Grilled Salmon",
        "Price": 32.0,
        "Availability": True,
    }


def test_get_invalid_menu_item():
    response = client.get("/restaurants/1/menu/Pizza")
    assert response.status_code == 404
    assert response.json()["detail"] == "Menu item not found"


def test_get_menu_item_invalid_restaurant():
    response = client.get("/restaurants/-1/menu/Duck Confit")
    assert response.status_code == 404
    assert response.json()["detail"] == "Restaurant not found"
