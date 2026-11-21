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


def test_owner_can_only_retrieve_the_restaurant_for_their_session(
    temporary_account_files,
):
    _, first_session = register_owner("first-profile-owner", "First Restaurant")
    _, second_session = register_owner("second-profile-owner", "Second Restaurant")

    first_profile = client.get(
        "/restaurant-owners/me",
        headers={"Authorization": f"Bearer {first_session['accessToken']}"},
    ).json()
    second_profile = client.get(
        "/restaurant-owners/me",
        headers={"Authorization": f"Bearer {second_session['accessToken']}"},
    ).json()

    assert first_profile["restaurantId"] == first_session["restaurantId"]
    assert first_profile["restaurant"]["Name"] == "First Restaurant"
    assert second_profile["restaurantId"] == second_session["restaurantId"]
    assert second_profile["restaurant"]["Name"] == "Second Restaurant"
    assert first_profile["restaurantId"] != second_profile["restaurantId"]


def test_owner_profile_returns_latest_saved_restaurant_details(
    temporary_account_files,
):
    _, session = register_owner("latest-profile-owner", "Original Restaurant")
    headers = {"Authorization": f"Bearer {session['accessToken']}"}
    updated_data = {
        "Name": "Latest Restaurant Name",
        "Cuisine": "Updated Cuisine",
        "Address": "25 New Street",
        "Hours": "11:00 AM - 9:00 PM",
        "Photos": ["https://example.com/latest.jpg"],
        "menu": [{"Name": "New Dish", "Price": 12.5, "Availability": True}],
    }

    update_response = client.put(
        f"/restaurants/{session['restaurantId']}",
        json=updated_data,
        headers=headers,
    )
    assert update_response.status_code == 201

    profile_response = client.get("/restaurant-owners/me", headers=headers)

    assert profile_response.status_code == 200
    assert profile_response.json()["restaurant"] == updated_data


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


def test_deactivation_requires_authenticated_owner(temporary_account_files):
    response = client.post("/restaurant-owners/deactivate")

    assert response.status_code == 401


def test_deactivation_disables_owner_and_restaurant_persistently(
    temporary_account_files,
):
    owners_file, restaurants_file = temporary_account_files
    _, session = register_owner("deactivate-owner", "Restaurant to Deactivate")
    headers = {"Authorization": f"Bearer {session['accessToken']}"}
    restaurant_id = session["restaurantId"]

    response = client.post("/restaurant-owners/deactivate", headers=headers)

    assert response.status_code == 204
    owners = json.loads(owners_file.read_text(encoding="utf-8"))
    restaurants = json.loads(restaurants_file.read_text(encoding="utf-8"))
    owner_record = next(item for item in owners if item["ownerId"] == session["ownerId"])
    restaurant_record = next(
        item for item in restaurants if item["id"] == restaurant_id
    )
    assert owner_record["active"] is False
    assert restaurant_record["active"] is False

    assert client.post(
        "/restaurant-owners/login",
        json={"username": session["username"], "password": "StrongPass123"},
    ).status_code == 401
    assert client.get("/restaurant-owners/me", headers=headers).status_code == 401
    assert client.get("/restaurants/").json() == []
    assert client.get(f"/restaurants/{restaurant_id}").status_code == 404
    assert client.get(f"/restaurants/{restaurant_id}/menu").status_code == 404


def test_deactivated_account_cannot_deactivate_again(temporary_account_files):
    _, session = register_owner("deactivate-twice-owner", "Deactivated Restaurant")
    headers = {"Authorization": f"Bearer {session['accessToken']}"}

    assert client.post("/restaurant-owners/deactivate", headers=headers).status_code == 204
    assert client.post("/restaurant-owners/deactivate", headers=headers).status_code == 401
