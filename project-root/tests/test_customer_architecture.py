import json

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.api.routes import customer_endpoints
from app.repositories.customer_repo import customerRepo
from app.services.customer_service import customerService

client = TestClient(app)

SEED = [
    {
        "firstName": "Jane",
        "lastName": "Doe",
        "Address": "804 Acadamey Way, Kelowna, BC",
        "emailAddress": "Janedoe@gmail.com",
        "paymentMethod": "credit",
        "phoneNumber": "250 555 4567",
        "orderHistory": [],
        "active": True,
        "cId": 1,
        "username": "JDoe",
        # customer passwords are stored as pbkdf2 hashes, not plain text
        "password": customerService._hash_password("janeDoe"),
    }
]

def login(username="JDoe", password="janeDoe"):
    """Log in through the real /customer/login endpoint and return the Authorization header."""
    response = client.post("/customer/login", json={"username": username, "password": password})
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['accessToken']}"}

@pytest.fixture(autouse=True)
def temp_data(tmp_path, monkeypatch):
    """Point the app at a fresh temp file for every test. test.json is never touched."""
    data_file = tmp_path / "data.json"
    data_file.write_text(json.dumps(SEED))
    monkeypatch.setattr(customer_endpoints.customer.repo, "file_path", data_file)
    return data_file

def test_get_valid_customer():
    response = client.get("/customer/me", headers=login())
    assert response.status_code == 200
    assert response.json() == {
        "firstName": "Jane",
        "lastName": "Doe",
        "Address": "804 Acadamey Way, Kelowna, BC",
        "emailAddress": "Janedoe@gmail.com",
        "paymentMethod": "credit",
        "phoneNumber": "250 555 4567",
        "orderHistory": [],
        "active": True,
        "cId": 1,
    }

def test_get_invalid_customer(temp_data):
    headers = login()
    temp_data.write_text("[]")   # the account no longer exists
    response = client.get("/customer/me", headers=headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "customer not found"

def test_customer_login_uses_customer_credentials(temp_data):
    response = client.post(
        "/customer/login",
        json={"username": "JDoe", "password": "janeDoe"},
    )

    assert response.status_code == 200
    assert response.json()["accessToken"]

def test_customer_login_rejects_invalid_password(temp_data):
    response = client.post(
        "/customer/login",
        json={"username": "JDoe", "password": "wrong"},
    )

    assert response.status_code == 401

def test_create_and_update_restaurant(temp_data):
    new_cus = {
        "firstName": "Jane",
        "lastName": "Doe",
        "Address": "804 Acadamey Way, Kelowna, BC",
        "emailAddress": "Janedoe@gmail.com",
        "paymentMethod": "credit",
        "phoneNumber": "250 555 4567",
        "username": "JDoe1",
        "password": "janeDoe"

    }
    response = client.post("/customer/sign-up", json=new_cus)
    assert response.status_code == 201
    assert response.json()["firstName"] == "Jane"

    cusId = response.json()["cId"]
    update_data = {
        "firstName": "Bob",
        "lastName": "Doe",
        "Address": "804 Acadamey Way, Kelowna, BC",
        "emailAddress": "Janedoe@gmail.com",
        "paymentMethod": "credit",
        "phoneNumber": "250 555 4567",
        "username": "JDoe1Renamed",
        "password": "janeDoe",
        "active": True,
    }
    response = client.put("/customer/me", json=update_data, headers=login("JDoe1"))
    assert response.status_code == 201
    assert response.json()["firstName"] == "Bob"

def test_customer_me_requires_login():
    assert client.get("/customer/me").status_code == 401

def test_customer_me_rejects_unknown_token():
    response = client.get("/customer/me", headers={"Authorization": "Bearer not-a-real-token"})
    assert response.status_code == 401

def test_update_customer_requires_login():
    assert client.put("/customer/me", json={}).status_code == 401

def test_login_token_works_on_protected_routes():
    login = client.post("/customer/login", json={"username": "JDoe", "password": "janeDoe"})
    assert login.status_code == 200
    body = login.json()
    assert body["cId"] == 1
    assert body["tokenType"] == "bearer"
    headers = {"Authorization": f"Bearer {body['accessToken']}"}
    me = client.get("/customer/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["cId"] == 1

def test_logout_invalidates_the_token():
    token = client.post("/customer/login", json={"username": "JDoe", "password": "janeDoe"}).json()["accessToken"]
    headers = {"Authorization": f"Bearer {token}"}
    assert client.post("/customer/logout", headers=headers).status_code == 204
    assert client.get("/customer/me", headers=headers).status_code == 401