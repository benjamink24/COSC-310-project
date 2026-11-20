import json

import pytest
from fastapi.testclient import TestClient

from app.api.routes import restaurant_owner_endpoints
from app.main import app

client = TestClient(app)


@pytest.fixture
def temporary_owner_data(tmp_path, monkeypatch):
    owners_file = tmp_path / "restaurant_owners.json"
    restaurants_file = tmp_path / "restaurants.json"
    restaurants_file.write_text("[]", encoding="utf-8")
    monkeypatch.setattr(restaurant_owner_endpoints.owner.repo, "file_path", owners_file)
    monkeypatch.setattr(
        restaurant_owner_endpoints.owner.restaurant_repo,
        "file_path",
        restaurants_file,
    )
    return owners_file, restaurants_file


def registration_payload():
    return {
        "firstName": "Rita",
        "lastName": "Owner",
        "Address": "10 Example Street",
        "emailAddress": "rita@example.com",
        "phoneNumber": "250-555-0100",
        "username": "rita-owner",
        "password": "StrongPass123",
        "restaurant": {
            "Name": "Rita's Kitchen",
            "Cuisine": "Italian",
            "Address": "12 Main Street",
            "Hours": "9:00 AM - 5:00 PM",
            "Photos": [],
            "menu": [],
        },
    }


def test_registration_persists_owner_and_associated_restaurant(temporary_owner_data):
    owners_file, restaurants_file = temporary_owner_data

    response = client.post(
        "/restaurant-owners/register",
        json=registration_payload(),
    )

    assert response.status_code == 201
    result = response.json()
    assert result["ownerId"] == 1
    assert result["restaurantId"] == 1
    assert result["restaurant"]["Name"] == "Rita's Kitchen"

    owners = json.loads(owners_file.read_text(encoding="utf-8"))
    restaurants = json.loads(restaurants_file.read_text(encoding="utf-8"))
    assert owners[0]["restaurantId"] == restaurants[0]["id"]
    assert restaurants[0]["ownerId"] == owners[0]["ownerId"]
    assert owners[0]["Address"] == registration_payload()["Address"]
    assert "password" not in owners[0]
    assert owners[0]["passwordHash"] != registration_payload()["password"]
    assert "password" not in result


def test_registration_rejects_duplicate_username(temporary_owner_data):
    payload = registration_payload()
    assert client.post("/restaurant-owners/register", json=payload).status_code == 201

    response = client.post("/restaurant-owners/register", json=payload)

    assert response.status_code == 409


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("emailAddress", "not-an-email"),
        ("username", "  "),
        ("Address", "  "),
        ("password", "short"),
    ],
)
def test_registration_validates_owner_information(
    temporary_owner_data, field, value
):
    payload = registration_payload()
    payload[field] = value

    response = client.post("/restaurant-owners/register", json=payload)

    assert response.status_code == 422


def test_registration_validates_required_restaurant_information(temporary_owner_data):
    payload = registration_payload()
    payload["restaurant"]["Name"] = " "

    response = client.post("/restaurant-owners/register", json=payload)

    assert response.status_code == 422


def test_registered_owner_can_log_in(temporary_owner_data):
    payload = registration_payload()
    client.post("/restaurant-owners/register", json=payload)

    response = client.post(
        "/restaurant-owners/login",
        json={"username": payload["username"], "password": payload["password"]},
    )

    assert response.status_code == 200
    assert response.json()["role"] == "restaurant"
    assert response.json()["restaurantId"] == 1
    assert response.json()["accessToken"]
    assert response.json()["tokenType"] == "bearer"

