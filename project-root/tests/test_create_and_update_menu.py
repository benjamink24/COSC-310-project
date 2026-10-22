import os
import json
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_menu_operations():
    # 1. Add a menu item using capitalized keys matching menu_model
    menu_item = {"Name": "Truffle Fries", "Price": 10.50, "Availability": True}
    response = client.post("/restaurants/6/menu", json=menu_item)
    assert response.status_code == 201

    # Verify the item is in the menu
    restaurant_data = response.json()
    added_item = next(
        (item for item in restaurant_data["menu"] if item["Name"] == "Truffle Fries"),
        None,
    )
    assert added_item is not None
    assert added_item["Price"] == 10.50

    # 2. Update the menu item
    updated_menu_item = {"Name": "Truffle Fries", "Price": 12.00, "Availability": False}
    response = client.put("/restaurants/6/menu/Truffle Fries", json=updated_menu_item)
    assert response.status_code == 200

    updated_data = response.json()
    modified_item = next(
        (item for item in updated_data["menu"] if item["Name"] == "Truffle Fries"), None
    )
    assert modified_item["Price"] == 12.00
    assert modified_item["Availability"] is False
