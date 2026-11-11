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
        "cId": 1
    }
]

@pytest.fixture(autouse=True)
def temp_data(tmp_path, monkeypatch):
    """Point the app at a fresh temp file for every test. test.json is never touched."""
    data_file = tmp_path / "data.json"
    data_file.write_text(json.dumps(SEED))
    monkeypatch.setattr(customer_endpoints.customer.repo, "file_path", data_file)
    return data_file




def test_get_valid_customer():
    response = client.get("/customer/1")
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
                "cId": 1
    }



def test_get_invalid_customer():
    response = client.get("/customer/-1")
    assert response.status_code == 404
    assert response.json()["detail"] == "customer not found"


def test_create_and_update_restaurant(temp_data):
    new_cus = {
        "firstName": "Joes",
        "lastName": "Doe",
        "Address": "804 Acadamey Way, Kelowna, BC",
        "emailAddress": "Janedoe@gmail.com",
        "paymentMethod": "credit",
        "phoneNumber": "250 555 4567"
    }
    response = client.post("/customer/", json=new_cus)
    assert response.status_code == 201
    assert response.json()["firstName"] == "Joes"
    
    cusId= response.json()["cId"]
    update_data = {
        "firstName": "Test Bistro Updated",
        "lastName": "Doe",
        "Address": "804 Acadamey Way, Kelowna, BC",
        "emailAddress": "Janedoe@gmail.com",
        "paymentMethod": "credit",
        "phoneNumber": "250 555 4567",
        "active": True
    }
    response = client.put(f"/customer/{cusId}", json=update_data)
    assert response.status_code == 201
    assert response.json()["firstName"] == "Test Bistro Updated"