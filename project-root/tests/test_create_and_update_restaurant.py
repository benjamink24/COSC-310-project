import os
import json
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_create_and_update_restaurant():
    # 1. Create a restaurant with unique test ID 999
    new_res = {
        "id": 999,
        "Name": "Test Bistro",
        "Cuisine": "Fusion",
        "Address": "123 Test St",
        "Hours": "9:00 AM - 5:00 PM",
        "Photos": [],
        "menu": [],
    }
    response = client.post("/restaurants", json=new_res)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 999
    assert data["Name"] == "Test Bistro"

    # 2. Update the restaurant
    update_data = {
        "id": 999,
        "Name": "Test Bistro Updated",
        "Cuisine": "Modern Fusion",
        "Address": "456 New St",
        "Hours": "10:00 AM - 6:00 PM",
        "Photos": [],
        "menu": [],
    }
    response = client.put("/restaurants/999", json=update_data)
    assert response.status_code == 200
    assert response.json()["Name"] == "Test Bistro Updated"
