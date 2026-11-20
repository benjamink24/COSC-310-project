import json

import pytest
from fastapi.testclient import TestClient

from app.api.routes import restaurant_endpoints, restaurant_owner_endpoints
from app.main import app

client = TestClient(app)


@pytest.fixture
def temporary_account_files(tmp_path, monkeypatch):
    owners_file = tmp_path / "restaurant_owners.json"
    restaurants_file = tmp_path / "restaurants.json"
    restaurants_file.write_text("[]", encoding="utf-8")
    monkeypatch.setattr(restaurant_owner_endpoints.owner.repo, "file_path", owners_file)
    monkeypatch.setattr(
        restaurant_owner_endpoints.owner.restaurant_repo,
        "file_path",
        restaurants_file,
    )
    monkeypatch.setattr(restaurant_endpoints.restaurant.repo, "file_path", restaurants_file)
    restaurant_owner_endpoints.owner._sessions.clear()
    return owners_file, restaurants_file


def register_owner(username: str, restaurant_name: str):
    payload = {
        "firstName": "Test",
        "lastName": "Owner",
        "Address": "10 Example Street",
        "emailAddress": f"{username}@example.com",
        "phoneNumber": "250-555-0100",
        "username": username,
        "password": "StrongPass123",
        "restaurant": {
            "Name": restaurant_name,
            "Cuisine": "Test",
            "Address": "1 Restaurant Street",
            "Hours": "9:00 AM - 5:00 PM",
            "Photos": [],
            "menu": [],
        },
    }
    response = client.post("/restaurant-owners/register", json=payload)
    assert response.status_code == 201
    login = client.post(
        "/restaurant-owners/login",
        json={"username": username, "password": payload["password"]},
    )
    assert login.status_code == 200
    return payload, login.json()


def restaurant_update(name: str):
    return {
        "Name": name,
        "Cuisine": "Test",
        "Address": "1 Restaurant Street",
        "Hours": "9:00 AM - 5:00 PM",
        "Photos": [],
        "menu": [],
    }


def test_invalid_owner_password_is_rejected(temporary_account_files):
    payload, _ = register_owner("first-owner", "First Restaurant")

    response = client.post(
        "/restaurant-owners/login",
        json={"username": payload["username"], "password": "wrong-password"},
    )

    assert response.status_code == 401


def test_owner_profile_requires_valid_session_and_hides_password(temporary_account_files):
    _, session = register_owner("profile-owner", "Profile Restaurant")

    assert client.get("/restaurant-owners/me").status_code == 401
    response = client.get(
        "/restaurant-owners/me",
        headers={"Authorization": f"Bearer {session['accessToken']}"},
    )

    assert response.status_code == 200
    profile = response.json()
    assert profile["ownerId"] == session["ownerId"]
    assert profile["restaurantId"] == session["restaurantId"]
    assert "password" not in profile
    assert "passwordHash" not in profile


def test_restaurant_update_requires_owning_owner_session(temporary_account_files):
    _, first_session = register_owner("first-owner", "First Restaurant")
    _, second_session = register_owner("second-owner", "Second Restaurant")
    restaurant_id = first_session["restaurantId"]

    response = client.put(
        f"/restaurants/{restaurant_id}",
        json=restaurant_update("Unauthorized Update"),
    )
    assert response.status_code == 401

    response = client.put(
        f"/restaurants/{restaurant_id}",
        json=restaurant_update("Wrong Owner Update"),
        headers={"Authorization": f"Bearer {second_session['accessToken']}"},
    )
    assert response.status_code == 403

    response = client.put(
        f"/restaurants/{restaurant_id}",
        json=restaurant_update("Authorized Update"),
        headers={"Authorization": f"Bearer {first_session['accessToken']}"},
    )
    assert response.status_code == 201
    assert response.json()["Name"] == "Authorized Update"

    response = client.post(
        f"/restaurants/{restaurant_id}/menu",
        json={"Name": "Unauthorized Item", "Price": 1, "Availability": True},
        headers={"Authorization": f"Bearer {second_session['accessToken']}"},
    )
    assert response.status_code == 403


def test_restaurant_creation_requires_owner_session(temporary_account_files):
    response = client.post(
        "/restaurants",
        json=restaurant_update("Unauthorized Restaurant"),
    )

    assert response.status_code == 401


def test_logout_revokes_owner_session(temporary_account_files):
    _, session = register_owner("logout-owner", "Logout Restaurant")
    headers = {"Authorization": f"Bearer {session['accessToken']}"}

    response = client.post("/restaurant-owners/logout", headers=headers)
    assert response.status_code == 204
    assert client.get("/restaurant-owners/me", headers=headers).status_code == 401


def test_owner_password_hash_is_persisted(temporary_account_files):
    owners_file, _ = temporary_account_files
    payload = {
        "firstName": "Hash",
        "lastName": "Check",
        "Address": "10 Example Street",
        "emailAddress": "hash-check@example.com",
        "phoneNumber": "250-555-0100",
        "username": "hash-check",
        "password": "StrongPass123",
        "restaurant": {
            "Name": "Hash Restaurant",
            "Cuisine": "Test",
            "Address": "1 Restaurant Street",
            "Hours": "9:00 AM - 5:00 PM",
            "Photos": [],
            "menu": [],
        },
    }

    response = client.post("/restaurant-owners/register", json=payload)

    assert response.status_code == 201
    owner = json.loads(owners_file.read_text(encoding="utf-8"))[0]
    assert owner["passwordHash"].startswith("pbkdf2_sha256$")
    assert owner["passwordHash"] != payload["password"]
    assert "password" not in owner


def test_expired_owner_session_is_rejected(temporary_account_files):
    _, session = register_owner("expired-owner", "Expired Restaurant")
    token = session["accessToken"]
    token_key = restaurant_owner_endpoints.owner._token_key(token)
    restaurant_owner_endpoints.owner._sessions[token_key]["expiresAt"] = 0

    response = client.get(
        "/restaurant-owners/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
