import json

import pytest
from fastapi.testclient import TestClient

from app.api.routes import customer_endpoints, checkout_endpoints, cart_endpoints
from app.main import app

client = TestClient(app)


@pytest.fixture
def temporary_account_files(tmp_path, monkeypatch):
    customer_file = tmp_path / "customers.json"
    customer_file.write_text("[]", encoding="utf-8")
    monkeypatch.setattr(customer_endpoints.customer.repo, "file_path", customer_file)
    customer_endpoints.customer._sessions.clear()
    return customer_file

def register_customer(username: str):
    payload = {
        "firstName": "Jane",
        "lastName": "Doe",
        "Address": "804 Acadamey Way, Kelowna, BC",
        "emailAddress": f"{username}@example.com",
        "paymentMethod": "credit",
        "phoneNumber": "250 555 4567",
        "username": username,
        "password": "janeDoe",
        
    }
    response = client.post("/customer/sign-up", json=payload)
    assert response.status_code == 201
    login = client.post(
        "/customer/login",
        json={"username": username, "password": payload["password"]},
    )
    assert login.status_code == 200
    return payload, login.json()


    

def test_invalid_customer_password_is_rejected(temporary_account_files):
    payload, _ = register_customer("johnySilverhand")

    response = client.post(
        "/customer/login",
        json={"username": payload["username"], "password": "wrong-password"},
    )

    assert response.status_code == 401


def test_customer_profile_requires_valid_session_and_hides_password(temporary_account_files):
    _, session = register_customer("profile-customer")

    assert client.get("/customer/me").status_code == 401
    response = client.get(
        "/customer/me",
        headers={"Authorization": f"Bearer {session['accessToken']}"},
    )

    assert response.status_code == 200
    profile = response.json()
    assert profile["cId"] == session["cId"]
    assert "password" not in profile
    assert "passwordHash" not in profile


def test_customer_no_credentials_rejected(temporary_account_files):
    customer_1_updated =  {
                    "firstName": "Jane",
                    "lastName": "Doe",
                    "Address": "804 Acadamey Way, Kelowna, BC",
                    "emailAddress": "hey@example.com",
                    "paymentMethod": "credit",
                    "phoneNumber": "250 555 4567",
                    "username": "first-customerupdated",
                    "password": "janeDoe",
                    "active": True
                            
                }
    # no credentials
    response = client.put(
        f"/customer/me",
        json=customer_1_updated,
    )
    assert response.status_code == 401

def test_logout_revokes_owner_session(temporary_account_files):
    _, session = register_customer("logout-owner")
    headers = {"Authorization": f"Bearer {session['accessToken']}"}

    response = client.post("/customer/logout", headers=headers)
    assert response.status_code == 204
    assert client.get("/customer/me", headers=headers).status_code == 401


def test_owner_password_hash_is_persisted(temporary_account_files):
    customer = temporary_account_files
    payload = {
        "firstName": "Jane",
        "lastName": "Doe",
        "Address": "804 Acadamey Way, Kelowna, BC",
        "emailAddress": "hey@example.com",
        "paymentMethod": "credit",
        "phoneNumber": "250 555 4567",
        "username": "first-customer",
        "password": "passwordHash",
    }
    

    response = client.post("/customer/sign-up", json=payload)

    assert response.status_code == 201
    owner = json.loads(customer.read_text(encoding="utf-8"))[0]
    assert owner["password"].startswith("pbkdf2_sha256$")
    assert owner["password"] != payload["password"]
    


def test_expired_owner_session_is_rejected(temporary_account_files):
    _, session = register_customer("expired-owner")
    token = session["accessToken"]
    token_key = customer_endpoints.customer._token_key(token)
    customer_endpoints.customer._sessions[token_key]["expiresAt"] = 0

    response = client.get(
        "/customer/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401


