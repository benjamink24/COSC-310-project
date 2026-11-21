import json

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.api.routes import customer_endpoints
from app.repositories.customer_repo import customerRepo

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
        "password": "janeDoe",
    }
]


@pytest.fixture(autouse=True)
def temp_data(tmp_path, monkeypatch):
    """Point the app at a fresh temp file for every test. test.json is never touched."""
    data_file = tmp_path / "data.json"
    data_file.write_text(json.dumps(SEED))
    monkeypatch.setattr(customer_endpoints.customer.repo, "file_path", data_file)
    return data_file


def test_valid_payment_method():
    new_cus = {
            "firstName": "Jane",
            "lastName": "Doe",
            "Address": "804 Acadamey Way, Kelowna, BC",
            "emailAddress": "Janedoe@gmail.com",
            "paymentMethod": "cash",
            "phoneNumber": "250 555 4567",
            "username": "JDoe1",
            "password": "janeDoe"
    
        }
    response = client.post("/customer/sign-up", json=new_cus)
    assert response.status_code == 422
    new_cus = {
                "firstName": "Jane",
                "lastName": "Doe",
                "Address": "804 Acadamey Way, Kelowna, BC",
                "emailAddress": "Janedoe@gmail.com",
                "paymentMethod": "credit",
                "phoneNumber": "250 555 4567",
                "username": "JDoe2",
                "password": "janeDoe"
        
            }
    response = client.post("/customer/sign-up", json=new_cus)
    assert response.status_code == 201

def test_validate_email():
    new_cus = {
            "firstName": "Jane",
            "lastName": "Doe",
            "Address": "804 Acadamey Way, Kelowna, BC",
            "emailAddress": "hi",
            "paymentMethod": "credit",
            "phoneNumber": "250 555 4567",
            "username": "JDoe3",
            "password": "janeDoe"
    
        }
    response = client.post("/customer/sign-up", json=new_cus)
    assert response.status_code == 422
    new_cus = {
                "firstName": "Jane",
                "lastName": "Doe",
                "Address": "804 Acadamey Way, Kelowna, BC",
                "emailAddress": "Janedoe@gmail.com",
                "paymentMethod": "credit",
                "phoneNumber": "250 555 4567",
                "username": "JDoe4",
                "password": "janeDoe"
        
            }
    response = client.post("/customer/sign-up", json=new_cus)
    assert response.status_code == 201

def test_validate_password():
    new_cus = {
            "firstName": "Jane",
            "lastName": "Doe",
            "Address": "804 Acadamey Way, Kelowna, BC",
            "emailAddress": "Janedoe@gmail.com",
            "paymentMethod": "credit",
            "phoneNumber": "250 555 4567",
            "username": "JDoe5",
            "password": "janedo"
    
        }
    response = client.post("/customer/sign-up", json=new_cus)
    assert response.status_code == 422
    new_cus = {
                "firstName": "Jane",
                "lastName": "Doe",
                "Address": "804 Acadamey Way, Kelowna, BC",
                "emailAddress": "Janedoe@gmail.com",
                "paymentMethod": "credit",
                "phoneNumber": "250 555 4567",
                "username": "JDoe6",
                "password": "DDDD"
        
            }
    response = client.post("/customer/sign-up", json=new_cus)
    assert response.status_code == 422
    
    new_cus = {
                "firstName": "Jane",
                "lastName": "Doe",
                "Address": "804 Acadamey Way, Kelowna, BC",
                "emailAddress": "Janedoe@gmail.com",
                "paymentMethod": "credit",
                "phoneNumber": "250 555 4567",
                "username": "JDoe7",
                "password": "janeDoe"
        
            }
    response = client.post("/customer/sign-up", json=new_cus)
    assert response.status_code == 201

def test_validate_username():
    new_cus = {
            "firstName": "Jane",
            "lastName": "Doe",
            "Address": "804 Acadamey Way, Kelowna, BC",
            "emailAddress": "Janedoe@gmail.com",
            "paymentMethod": "credit",
            "phoneNumber": "250 555 4567",
            "username": "JDoe8",
            "password": "janeDoe"
    
        }
    response = client.post("/customer/sign-up", json=new_cus)
    assert response.status_code == 201
    new_cus = {
                "firstName": "Jane",
                "lastName": "Doe",
                "Address": "804 Acadamey Way, Kelowna, BC",
                "emailAddress": "Janedoe@gmail.com",
                "paymentMethod": "credit",
                "phoneNumber": "250 555 4567",
                "username": "JDoe8",
                "password": "janeDoe"
        
            }
    response = client.post("/customer/sign-up", json=new_cus)
    assert response.status_code == 422


    