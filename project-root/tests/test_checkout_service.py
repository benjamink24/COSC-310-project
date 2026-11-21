"""Unit tests for checkoutService: real repositories on temp JSON files, no HTTP."""
import json
from datetime import datetime
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.repositories.cart_repo import cartRepo
from app.repositories.customer_repo import customerRepo
from app.repositories.history_repo import histRepo
from app.repositories.restaurant_repo import resRepo
from app.services.checkout_service import checkoutService

CUSTOMER_SEED = [
    {"cId": 1, "firstName": "Jane", "active": True},
    {"cId": 3, "firstName": "Sam", "active": True},
]

def make_restaurants():
    return [
        {
            "id": 1,
            "Name": "Waterfront Wines",
            "menu": [
                {"Name": "Grilled Salmon", "Price": 32.0, "Availability": True},
                {"Name": "Beef Tenderloin", "Price": 42.0, "Availability": True},
                {"Name": "Cookie", "Price": 0.1, "Availability": True},
            ],
        },
        {
            "id": 2,
            "Name": "Bohemian Cafe",
            "menu": [{"Name": "French Toast", "Price": 16.0, "Availability": True}],
        },
    ]

@pytest.fixture
def repos(tmp_path):
    files = {name: tmp_path / f"{name}.json" for name in ("cart", "history", "customers", "restaurants")}
    files["cart"].write_text("[]")
    files["history"].write_text("[]")
    files["customers"].write_text(json.dumps(CUSTOMER_SEED))
    files["restaurants"].write_text(json.dumps(make_restaurants()))
    return SimpleNamespace(
        files=files,
        cart=cartRepo(files["cart"]),
        history=histRepo(files["history"]),
        customer=customerRepo(files["customers"]),
        res=resRepo(files["restaurants"]),
    )

@pytest.fixture
def service(repos):
    return checkoutService(
        cart_repo=repos.cart,
        history_repo=repos.history,
        customer_repo=repos.customer,
        res_repo=repos.res,
    )

def put_in_cart(repos, cId=1, restaurantId=1, items=None):
    """Writes a cart straight into the cart file, as cartService would have."""
    if items is None:
        items = [{"Name": "Grilled Salmon", "Price": 32.0, "quantity": 2}]
    repos.cart.save_cart({"cId": cId, "restaurantId": restaurantId, "items": items})

def change_restaurants(repos, change):
    restaurants = json.loads(repos.files["restaurants"].read_text())
    change(restaurants)
    repos.files["restaurants"].write_text(json.dumps(restaurants))

# ---------- a successful checkout ----------
def test_checkout_returns_the_saved_order(service, repos):
    put_in_cart(repos, items=[
        {"Name": "Grilled Salmon", "Price": 32.0, "quantity": 2},
        {"Name": "Beef Tenderloin", "Price": 42.0, "quantity": 1},
    ])
    order = service.checkout(1, "credit")

    assert order["orderId"] == 1
    assert order["cId"] == 1
    assert order["restaurantId"] == 1
    assert order["paymentMethod"] == "credit"
    assert order["status"] == "placed"
    assert order["total"] == 106.0
    assert order["items"] == [
        {"Name": "Grilled Salmon", "Price": 32.0, "quantity": 2},
        {"Name": "Beef Tenderloin", "Price": 42.0, "quantity": 1},
    ]
    datetime.fromisoformat(order["timestamp"])   # must be a valid ISO timestamp

def test_checkout_saves_the_order_in_history(service, repos):
    put_in_cart(repos)
    order = service.checkout(1, "credit")
    assert repos.history.get_all() == [order]

def test_checkout_empties_the_cart(service, repos):
    put_in_cart(repos)
    service.checkout(1, "credit")
    assert repos.cart.get_cart_by_cid(1) is None

def test_checkout_leaves_other_customers_carts_alone(service, repos):
    put_in_cart(repos, cId=1)
    put_in_cart(repos, cId=3, restaurantId=2, items=[{"Name": "French Toast", "Price": 16.0, "quantity": 1}])
    service.checkout(1, "credit")
    assert repos.cart.get_cart_by_cid(3) is not None

def test_order_total_is_rounded_to_two_decimals(service, repos):
    put_in_cart(repos, items=[{"Name": "Cookie", "Price": 0.1, "quantity": 3}])
    assert service.checkout(1, "debit")["total"] == 0.3

# ---------- prices come from the menu at checkout time ----------
def test_order_uses_the_current_menu_price(service, repos):
    put_in_cart(repos, items=[{"Name": "Grilled Salmon", "Price": 32.0, "quantity": 2}])

    def raise_price(restaurants):
        restaurants[0]["menu"][0]["Price"] = 35.0

    change_restaurants(repos, raise_price)

    order = service.checkout(1, "credit")
    assert order["items"][0]["Price"] == 35.0
    assert order["total"] == 70.0

def test_order_uses_the_menu_spelling_of_item_names(service, repos):
    put_in_cart(repos, items=[{"Name": "grilled salmon", "Price": 32.0, "quantity": 1}])
    assert service.checkout(1, "credit")["items"][0]["Name"] == "Grilled Salmon"

# ---------- refused checkouts change nothing ----------
def test_checkout_for_unknown_customer_raises_404_and_writes_nothing(service, repos):
    put_in_cart(repos, cId=99)
    with pytest.raises(HTTPException) as error:
        service.checkout(99, "credit")
    assert (error.value.status_code, error.value.detail) == (404, "customer not found")
    assert repos.history.get_all() == []

def test_checkout_with_no_cart_raises_400(service, repos):
    with pytest.raises(HTTPException) as error:
        service.checkout(1, "credit")
    assert (error.value.status_code, error.value.detail) == (400, "cart is empty")
    assert repos.history.get_all() == []

def test_checkout_with_an_empty_cart_raises_400(service, repos):
    put_in_cart(repos, items=[])
    with pytest.raises(HTTPException) as error:
        service.checkout(1, "credit")
    assert error.value.status_code == 400
    assert repos.history.get_all() == []

def test_checkout_with_a_sold_out_item_raises_409_and_keeps_the_cart(service, repos):
    put_in_cart(repos)

    def sell_out(restaurants):
        restaurants[0]["menu"][0]["Availability"] = False

    change_restaurants(repos, sell_out)

    with pytest.raises(HTTPException) as error:
        service.checkout(1, "credit")
    assert error.value.status_code == 409
    assert "no longer available" in error.value.detail
    assert repos.history.get_all() == []
    assert repos.cart.get_cart_by_cid(1) is not None

def test_checkout_with_an_item_removed_from_the_menu_raises_409(service, repos):
    put_in_cart(repos)

    def remove_salmon(restaurants):
        restaurants[0]["menu"] = [i for i in restaurants[0]["menu"] if i["Name"] != "Grilled Salmon"]

    change_restaurants(repos, remove_salmon)

    with pytest.raises(HTTPException) as error:
        service.checkout(1, "credit")
    assert error.value.status_code == 409
    assert "no longer on the menu" in error.value.detail
    assert repos.history.get_all() == []

def test_checkout_when_the_restaurant_is_gone_raises_409(service, repos):
    put_in_cart(repos)
    change_restaurants(repos, lambda restaurants: restaurants.pop(0))

    with pytest.raises(HTTPException) as error:
        service.checkout(1, "credit")
    assert (error.value.status_code, error.value.detail) == (409, "restaurant no longer exists")
    assert repos.history.get_all() == []

def test_cart_is_kept_if_saving_the_order_fails(service, repos):
    # the order is saved first and the cart cleared second, so a failed save loses nothing
    put_in_cart(repos)

    def broken_add_order(order):
        raise RuntimeError("disk full")

    repos.history.add_order = broken_add_order

    with pytest.raises(RuntimeError):
        service.checkout(1, "credit")
    assert repos.cart.get_cart_by_cid(1) is not None

# ---------- order ids ----------
def test_order_ids_count_up_across_checkouts(service, repos):
    put_in_cart(repos)
    first = service.checkout(1, "credit")
    put_in_cart(repos)
    second = service.checkout(1, "credit")
    assert (first["orderId"], second["orderId"]) == (1, 2)

def test_order_ids_are_shared_across_customers(service, repos):
    put_in_cart(repos, cId=1)
    put_in_cart(repos, cId=3, restaurantId=2, items=[{"Name": "French Toast", "Price": 16.0, "quantity": 1}])
    first = service.checkout(1, "credit")
    second = service.checkout(3, "debit")
    assert (first["orderId"], second["orderId"]) == (1, 2)

# ---------- get_order_history ----------
def test_history_for_customer_with_no_orders_is_empty(service):
    assert service.get_order_history(1) == []

def test_history_returns_only_that_customers_orders_oldest_first(service, repos):
    put_in_cart(repos, cId=1)
    first = service.checkout(1, "credit")
    put_in_cart(repos, cId=3, restaurantId=2, items=[{"Name": "French Toast", "Price": 16.0, "quantity": 1}])
    service.checkout(3, "debit")
    put_in_cart(repos, cId=1, items=[{"Name": "Beef Tenderloin", "Price": 42.0, "quantity": 1}])
    third = service.checkout(1, "credit")

    assert service.get_order_history(1) == [first, third]
    assert [o["cId"] for o in service.get_order_history(3)] == [3]

def test_history_for_unknown_customer_raises_404(service):
    with pytest.raises(HTTPException) as error:
        service.get_order_history(99)
    assert (error.value.status_code, error.value.detail) == (404, "customer not found")