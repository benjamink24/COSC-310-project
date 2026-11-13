"""End-to-end: cart -> checkout -> history, through the real routes and real
repositories, with all four JSON files redirected to temp copies (see data_files below)."""
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
#   cart_endpoints.cart needs attributes cart_repo, res_repo, customer_repo
#   checkout_endpoints.checkout needs attributes cart_repo, history_repo, customer_repo, res_repo

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

def add_to_cart(client, cId=1, restaurantId=1, Name="Grilled Salmon", quantity=2):
    return client.post(
        f"/cart/{cId}/items",
        json={"restaurantId": restaurantId, "Name": Name, "quantity": quantity},
    )

def checkout(client, cId=1, paymentMethod="credit"):
    return client.post("/checkout/", json={"cId": cId, "paymentMethod": paymentMethod})

def read(path):
    return json.loads(path.read_text())

def edit_restaurants(path, change): # helper to edit the restaurants.json file in place
    restaurants = read(path)
    change(restaurants)
    path.write_text(json.dumps(restaurants))

def test_full_flow_cart_to_checkout_to_history():
    add_to_cart(client, Name="Grilled Salmon", quantity=2)
    add_to_cart(client, Name="Beef Tenderloin", quantity=1)
    assert client.get("/cart/1").json()["total"] == 106.0
    response = checkout(client)
    assert response.status_code == 201
    order = response.json()
    assert order["orderId"] == 1
    assert order["cId"] == 1
    assert order["restaurantId"] == 1
    assert order["total"] == 106.0
    assert order["status"] == "placed"
    assert len(order["items"]) == 2
    assert client.get("/cart/1").status_code == 404   # cart was cleared
    history = client.get("/checkout/history/1")
    assert history.status_code == 200
    assert history.json() == [order]

def test_second_order_gets_the_next_id():
    #   historyRepo.add_order sets orderId = last orderId + 1. Both orders then
    #   appear, oldest first, in GET /checkout/history/1.
    add_to_cart(client)
    first = checkout(client).json()
    add_to_cart(client, Name="Beef Tenderloin", quantity=1)
    second = checkout(client).json()

    assert (first["orderId"], second["orderId"]) == (1, 2)
    assert len(client.get("/checkout/history/1").json()) == 2

def test_can_order_from_another_restaurant_after_checkout():
    add_to_cart(client, restaurantId=1)
    checkout(client)
    response = add_to_cart(client, restaurantId=2, Name="French Toast", quantity=1)
    assert response.status_code == 201
    assert response.json()["restaurantId"] == 2

def test_customers_have_separate_carts_and_histories():
    # Sam's cart must still be there after Jane checks out.
    add_to_cart(client, cId=1, Name="Grilled Salmon", quantity=1)
    add_to_cart(client, cId=3, restaurantId=2, Name="French Toast", quantity=2)

    checkout(client, cId=1)
    assert client.get("/cart/3").status_code == 200       # Sam's cart untouched
    assert client.get("/checkout/history/3").json() == []

    checkout(client, cId=3)
    assert client.get("/checkout/history/1").json()[0]["total"] == 32.0
    assert client.get("/checkout/history/3").json()[0]["total"] == 32.0
    assert client.get("/checkout/history/3").json()[0]["restaurantId"] == 2

# ---------- refused checkouts must change nothing ----------
def test_checkout_with_no_cart_returns_400_and_writes_nothing(data_files):
    #runs a 400 error and history should be empty
    response = checkout(client)
    assert response.status_code == 400
    assert read(data_files["history"]) == []

def test_checkout_invalid_body_returns_422():
    #   checkout_request_model requires cId and a non-empty
    #   paymentMethod and FastAPI returns 422 when they are missing or empty.
    assert client.post("/checkout/", json={"cId": 1}).status_code == 422
    assert client.post("/checkout/", json={"paymentMethod": "credit"}).status_code == 422
    assert client.post("/checkout/", json={"cId": 1, "paymentMethod": ""}).status_code == 422

def test_price_change_after_adding_is_applied_at_checkout(data_files):
    #   The test changes Grilled Salmon from 32.0 to 35.0 after it was added
    #   order must use the NEW price: 2 x 35.0 = 70.0
    add_to_cart(client, Name="Grilled Salmon", quantity=2)

    def raise_price(restaurants):
        restaurants[0]["menu"][0]["Price"] = 35.0

    edit_restaurants(data_files["restaurants"], raise_price)

    order = checkout(client).json()
    assert order["items"][0]["Price"] == 35.0
    assert order["total"] == 70.0

# ---------- history endpoint ----------
def test_history_for_customer_with_no_orders_is_an_empty_list():
    response = client.get("/checkout/history/1")
    assert response.status_code == 200
    assert response.json() == []

def test_history_for_unknown_customer_returns_404():
    assert client.get("/checkout/history/99").status_code == 404

# ---------- regression guard for the existing customer routes ----------
def test_checkout_does_not_modify_the_customer_record(data_files):
    before = read(data_files["customers"])
    add_to_cart(client)
    checkout(client)

    assert read(data_files["customers"]) == before
    assert client.get("/customer/").status_code == 200