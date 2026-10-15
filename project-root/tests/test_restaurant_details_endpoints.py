import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.api.routes import restaurant_endpoints


class MockRepo:
    def get_all_restaurants(self):
        return [
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
                ],
            }
        ]


@pytest.fixture
def client(monkeypatch):
    # Swap in fake data so the tests don't depend on restaurants.json
    monkeypatch.setattr(restaurant_endpoints.restaurant, "repo", MockRepo())
    return TestClient(app)


# --- Restaurant details ---

def test_get_valid_restaurant(client):
    response = client.get("/restaurants/1")
    assert response.status_code == 200
    body = response.json()
    assert body["Name"] == "Waterfront Wines"
    assert body["Cuisine"] == "Farm-to-Table"
    assert body["Address"] == "1180 Sunset Dr #104, Kelowna, BC"
    assert body["Hours"] == "5:00 PM - 10:00 PM"
    assert "id" not in body
    assert "menu" not in body
    assert "Photos" not in body


def test_get_invalid_restaurant(client):
    response = client.get("/restaurants/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Restaurant not found"


# --- Menu ---

def test_get_valid_menu(client):
    response = client.get("/restaurants/1/menu")
    assert response.status_code == 200
    body = response.json()
    assert body["restaurant_id"] == 1
    assert body["restaurant_name"] == "Waterfront Wines"
    assert [item["id"] for item in body["items"]] == [1, 2]
    assert body["items"][0]["Name"] == "Grilled Salmon"


def test_get_menu_invalid_restaurant(client):
    response = client.get("/restaurants/999/menu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Restaurant not found"


# --- Menu item ---

def test_get_valid_menu_item(client):
    response = client.get("/restaurants/1/menu/2")
    assert response.status_code == 200
    assert response.json() == {
        "id": 2,
        "Name": "Duck Confit",
        "Price": 36.0,
        "Availability": False,
    }


def test_get_invalid_menu_item(client):
    response = client.get("/restaurants/1/menu/99")
    assert response.status_code == 404
    assert response.json()["detail"] == "Menu item not found"


def test_get_menu_item_invalid_restaurant(client):
    response = client.get("/restaurants/999/menu/1")
    assert response.status_code == 404
    assert response.json()["detail"] == "Restaurant not found"