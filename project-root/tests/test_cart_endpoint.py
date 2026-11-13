"""HTTP tests for /cart. Seeds its own temp data files (see data_files below)."""
import json

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.api.routes import cart_endpoints, checkout_endpoints, customer_endpoints

client = TestClient(app)

def _customer(cId, firstName):
    return {
        "cId": cId,
        "firstName": firstName,
        "lastName": "Doe",
        "Address": "804 Acadamey Way, Kelowna, BC",
        "emailAddress": f"{firstName.lower()}@example.com",
        "paymentMethod": "credit",
        "phoneNumber": "250 555 4567",
        "orderHistory": [],
        "active": True,
    }

CUSTOMER_SEED = [
    _customer(1, "Jane"),
    _customer(3, "Sam"),
]

RESTAURANT_SEED = [
    {
        "id": 1,
        "Name": "Waterfront Wines",
        "Cuisine": "Farm-to-Table",
        "Address": "1180 Sunset Dr #104, Kelowna, BC",
        "Hours": "5:00 PM - 10:00 PM",
        "Photos": [],
        "menu": [
            {"Name": "Grilled Salmon", "Price": 32.0, "Availability": True},
            {"Name": "Beef Tenderloin", "Price": 42.0, "Availability": True},
            {"Name": "Duck Confit", "Price": 36.0, "Availability": False},
        ],
    },
    {
        "id": 2,
        "Name": "Bohemian Cafe",
        "Cuisine": "Breakfast & Brunch",
        "Address": "572 Bernard Ave, Kelowna, BC",
        "Hours": "7:00 AM - 2:30 PM",
        "Photos": [],
        "menu": [{"Name": "French Toast", "Price": 16.0, "Availability": True}],
    },
]
@pytest.fixture(autouse=True)
def data_files(tmp_path, monkeypatch):
    """Give every test fresh temp copies of the four JSON files and point every
    repository at them. The real data/*.json files are never touched."""
    files = {
        name: tmp_path / f"{name}.json"
        for name in ("cart", "history", "customers", "restaurants")
    }
    files["cart"].write_text("[]")
    files["history"].write_text("[]")
    files["customers"].write_text(json.dumps(CUSTOMER_SEED))
    files["restaurants"].write_text(json.dumps(RESTAURANT_SEED))

    cart_service = cart_endpoints.cart
    checkout_service = checkout_endpoints.checkout
    targets = [
        (cart_service.cart_repo, "cart"),
        (cart_service.res_repo, "restaurants"),
        (cart_service.customer_repo, "customers"),
        (checkout_service.cart_repo, "cart"),
        (checkout_service.history_repo, "history"),
        (checkout_service.customer_repo, "customers"),
        (checkout_service.res_repo, "restaurants"),
        (customer_endpoints.customer.repo, "customers"),
    ]
    for repo, name in targets:
        monkeypatch.setattr(repo, "file_path", files[name])
    return files

def add(client, cId=1, restaurantId=1, Name="Grilled Salmon", quantity=2):
    return client.post(
        f"/cart/{cId}/items",
        json={"restaurantId": restaurantId, "Name": Name, "quantity": quantity},
    )

# ---------- GET /cart/{cId} ----------
def test_get_cart_with_no_cart_returns_404():
    response = client.get("/cart/1")
    assert response.status_code == 404
    assert response.json()["detail"] == "cart not found"

def test_get_cart_returns_what_was_added():
    add(client)
    response = client.get("/cart/1")
    assert response.status_code == 200
    assert response.json() == {
        "cId": 1,
        "restaurantId": 1,
        "items": [{"Name": "Grilled Salmon", "Price": 32.0, "quantity": 2}],
        "total": 64.0,
    }

# ---------- POST /cart/{cId}/items ----------
def test_add_item_returns_201_and_the_cart():
    response = add(client)
    assert response.status_code == 201
    body = response.json()
    assert body["cId"] == 1
    assert body["restaurantId"] == 1
    assert body["items"] == [{"Name": "Grilled Salmon", "Price": 32.0, "quantity": 2}]
    assert body["total"] == 64.0

@pytest.mark.parametrize(
    "body",
    [
        {"restaurantId": 1, "Name": "Grilled Salmon", "quantity": 0},
        {"restaurantId": 1, "Name": "Grilled Salmon", "quantity": -1},
        {"restaurantId": 1, "Name": "Grilled Salmon", "quantity": "two"},
        {"restaurantId": 1, "Name": "", "quantity": 1},
        {"restaurantId": 1, "quantity": 1},
        {"Name": "Grilled Salmon", "quantity": 1},
        {"restaurantId": 1, "Name": "Grilled Salmon"},
    ],
)
def test_add_item_invalid_body_returns_422(body):
    assert client.post("/cart/1/items", json=body).status_code == 422

def test_add_unavailable_item_returns_409():

    assert add(client, Name="Duck Confit", quantity=1).status_code == 409

def test_add_item_from_other_restaurant_returns_409_and_cart_is_unchanged():
    add(client, restaurantId=1)
    response = add(client, restaurantId=2, Name="French Toast", quantity=1)
    assert response.status_code == 409

    cart = client.get("/cart/1").json()
    assert cart["restaurantId"] == 1
    assert len(cart["items"]) == 1

def test_add_item_is_written_to_the_cart_file(data_files):
    add(client)
    saved = json.loads(data_files["cart"].read_text())
    assert len(saved) == 1
    assert saved[0]["cId"] == 1

# ---------- PUT /cart/{cId}/items/{item_name} ----------
def test_update_item_quantity():
    add(client, quantity=2)
    response = client.put("/cart/1/items/Grilled%20Salmon", json={"quantity": 5})
    assert response.status_code == 200
    assert response.json()["items"][0]["quantity"] == 5
    assert response.json()["total"] == 160.0

@pytest.mark.parametrize("bad_quantity", [0, -1, "two"])
def test_update_item_invalid_quantity_returns_422(bad_quantity):
    add(client)
    response = client.put("/cart/1/items/Grilled%20Salmon", json={"quantity": bad_quantity})
    assert response.status_code == 422

def test_update_item_not_in_cart_returns_404():
    add(client, Name="Grilled Salmon")
    response = client.put("/cart/1/items/Beef%20Tenderloin", json={"quantity": 2})
    assert response.status_code == 404

# ---------- DELETE /cart/{cId}/items/{item_name} ----------
def test_remove_item():
    add(client, Name="Grilled Salmon")
    add(client, Name="Beef Tenderloin", quantity=1)
    response = client.delete("/cart/1/items/Grilled%20Salmon")
    assert response.status_code == 200
    assert [i["Name"] for i in response.json()["items"]] == ["Beef Tenderloin"]

def test_remove_item_not_in_cart_returns_404():
    add(client, Name="Grilled Salmon")
    assert client.delete("/cart/1/items/Beef%20Tenderloin").status_code == 404

# ---------- DELETE /cart/{cId} ----------
def test_clear_cart_returns_204_and_removes_it():
    add(client)
    response = client.delete("/cart/1")
    assert response.status_code == 204
    assert client.get("/cart/1").status_code == 404

def test_clear_cart_with_no_cart_returns_404():
    assert client.delete("/cart/1").status_code == 404