"""Unit tests for cartService: real repositories on temp JSON files, no HTTP."""
import json
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.repositories.cart_repo import cartRepo
from app.repositories.customer_repo import customerRepo
from app.repositories.restaurant_repo import resRepo
from app.services.cart_service import cartService

CUSTOMER_SEED = [
    {"cId": 1, "firstName": "Jane", "active": True},
    {"cId": 3, "firstName": "Sam", "active": True},
]

RESTAURANT_SEED = [
    {
        "id": 1,
        "Name": "Waterfront Wines",
        "menu": [
            {"Name": "Grilled Salmon", "Price": 32.0, "Availability": True},
            {"Name": "Beef Tenderloin", "Price": 42.0, "Availability": True},
            {"Name": "Duck Confit", "Price": 36.0, "Availability": False},
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
    files = {name: tmp_path / f"{name}.json" for name in ("cart", "customers", "restaurants")}
    files["cart"].write_text("[]")
    files["customers"].write_text(json.dumps(CUSTOMER_SEED))
    files["restaurants"].write_text(json.dumps(RESTAURANT_SEED))
    return SimpleNamespace(
        cart=cartRepo(files["cart"]),
        customer=customerRepo(files["customers"]),
        res=resRepo(files["restaurants"]),
    )

@pytest.fixture
def service(repos):
    return cartService(cart_repo=repos.cart, res_repo=repos.res, customer_repo=repos.customer)

# ---------- get_cart ----------
def test_get_cart_with_no_cart_returns_none(service):
    assert service.get_cart(1) is None

def test_get_cart_returns_items_and_computed_total(service):
    service.add_item(1, 1, "Grilled Salmon", 2)
    assert service.get_cart(1) == {
        "cId": 1,
        "restaurantId": 1,
        "items": [{"Name": "Grilled Salmon", "Price": 32.0, "quantity": 2}],
        "total": 64.0,
    }

def test_get_cart_for_unknown_customer_raises_404(service):
    with pytest.raises(HTTPException) as error:
        service.get_cart(99)
    assert error.value.status_code == 404
    assert error.value.detail == "customer not found"

# ---------- add_item ----------
def test_add_item_creates_a_cart_with_the_menu_price(service):
    cart = service.add_item(1, 1, "Beef Tenderloin", 1)
    assert cart["items"] == [{"Name": "Beef Tenderloin", "Price": 42.0, "quantity": 1}]
    assert cart["total"] == 42.0

def test_add_same_item_again_increases_quantity(service):
    service.add_item(1, 1, "Grilled Salmon", 2)
    cart = service.add_item(1, 1, "Grilled Salmon", 3)
    assert cart["items"] == [{"Name": "Grilled Salmon", "Price": 32.0, "quantity": 5}]
    assert cart["total"] == 160.0

def test_item_names_match_ignoring_case_and_spaces(service):
    service.add_item(1, 1, "Grilled Salmon", 2)
    cart = service.add_item(1, 1, "  grilled salmon ", 1)
    assert len(cart["items"]) == 1
    assert cart["items"][0]["Name"] == "Grilled Salmon"   # the menu's spelling is kept
    assert cart["items"][0]["quantity"] == 3

def test_add_different_items_from_same_restaurant(service):
    service.add_item(1, 1, "Grilled Salmon", 1)
    cart = service.add_item(1, 1, "Beef Tenderloin", 2)
    assert [i["Name"] for i in cart["items"]] == ["Grilled Salmon", "Beef Tenderloin"]
    assert cart["total"] == 116.0

def test_total_is_rounded_to_two_decimals(service):
    cart = service.add_item(1, 1, "Cookie", 3)   # 0.1 * 3 is 0.30000000000000004 in floats
    assert cart["total"] == 0.3

def test_total_is_not_stored_in_the_cart_file(service, repos):
    service.add_item(1, 1, "Grilled Salmon", 2)
    assert "total" not in repos.cart.get_cart_by_cid(1)

def test_add_item_for_unknown_customer_raises_404(service):
    with pytest.raises(HTTPException) as error:
        service.add_item(99, 1, "Grilled Salmon", 1)
    assert (error.value.status_code, error.value.detail) == (404, "customer not found")

def test_add_item_for_unknown_restaurant_raises_404(service):
    with pytest.raises(HTTPException) as error:
        service.add_item(1, 99, "Grilled Salmon", 1)
    assert (error.value.status_code, error.value.detail) == (404, "restaurant not found")

def test_add_unknown_menu_item_raises_404(service):
    with pytest.raises(HTTPException) as error:
        service.add_item(1, 1, "Pizza", 1)
    assert (error.value.status_code, error.value.detail) == (404, "menu item not found")

def test_add_unavailable_item_raises_409_and_creates_no_cart(service, repos):
    with pytest.raises(HTTPException) as error:
        service.add_item(1, 1, "Duck Confit", 1)
    assert error.value.status_code == 409
    assert repos.cart.get_cart_by_cid(1) is None

def test_add_item_from_another_restaurant_raises_409_and_keeps_the_cart(service, repos):
    service.add_item(1, 1, "Grilled Salmon", 1)
    with pytest.raises(HTTPException) as error:
        service.add_item(1, 2, "French Toast", 1)
    assert error.value.status_code == 409

    cart = repos.cart.get_cart_by_cid(1)
    assert cart["restaurantId"] == 1
    assert [i["Name"] for i in cart["items"]] == ["Grilled Salmon"]

def test_emptied_cart_can_switch_to_another_restaurant(service):
    service.add_item(1, 1, "Grilled Salmon", 1)
    service.remove_item(1, "Grilled Salmon")
    cart = service.add_item(1, 2, "French Toast", 2)
    assert cart["restaurantId"] == 2
    assert [i["Name"] for i in cart["items"]] == ["French Toast"]

def test_customers_have_separate_carts(service):
    service.add_item(1, 1, "Grilled Salmon", 1)
    service.add_item(3, 2, "French Toast", 4)
    assert service.get_cart(1)["restaurantId"] == 1
    assert service.get_cart(3)["restaurantId"] == 2
    assert service.get_cart(3)["total"] == 64.0

# ---------- update_item ----------
def test_update_item_sets_the_quantity(service):
    service.add_item(1, 1, "Grilled Salmon", 2)
    cart = service.update_item(1, "Grilled Salmon", 5)   # sets, does not add
    assert cart["items"][0]["quantity"] == 5
    assert cart["total"] == 160.0

def test_update_item_ignores_name_case(service):
    service.add_item(1, 1, "Grilled Salmon", 2)
    assert service.update_item(1, "grilled salmon", 4)["items"][0]["quantity"] == 4

def test_update_item_with_no_cart_raises_404(service):
    with pytest.raises(HTTPException) as error:
        service.update_item(1, "Grilled Salmon", 2)
    assert (error.value.status_code, error.value.detail) == (404, "cart not found")

def test_update_item_not_in_cart_raises_404(service):
    service.add_item(1, 1, "Grilled Salmon", 1)
    with pytest.raises(HTTPException) as error:
        service.update_item(1, "Beef Tenderloin", 2)
    assert (error.value.status_code, error.value.detail) == (404, "item not in cart")

# ---------- remove_item ----------
def test_remove_item_removes_only_that_line(service):
    service.add_item(1, 1, "Grilled Salmon", 1)
    service.add_item(1, 1, "Beef Tenderloin", 1)
    cart = service.remove_item(1, "Grilled Salmon")
    assert [i["Name"] for i in cart["items"]] == ["Beef Tenderloin"]
    assert cart["total"] == 42.0

def test_removing_the_last_item_leaves_an_empty_cart(service):
    service.add_item(1, 1, "Grilled Salmon", 1)
    cart = service.remove_item(1, "Grilled Salmon")
    assert cart["items"] == []
    assert cart["total"] == 0
    assert service.get_cart(1) is not None  

def test_remove_item_with_no_cart_raises_404(service):
    with pytest.raises(HTTPException) as error:
        service.remove_item(1, "Grilled Salmon")
    assert (error.value.status_code, error.value.detail) == (404, "cart not found")

def test_remove_item_not_in_cart_raises_404_and_changes_nothing(service, repos):
    service.add_item(1, 1, "Grilled Salmon", 1)
    with pytest.raises(HTTPException) as error:
        service.remove_item(1, "Beef Tenderloin")
    assert (error.value.status_code, error.value.detail) == (404, "item not in cart")
    assert len(repos.cart.get_cart_by_cid(1)["items"]) == 1

# ---------- clear_cart ----------
def test_clear_cart_deletes_the_cart(service):
    service.add_item(1, 1, "Grilled Salmon", 1)
    assert service.clear_cart(1) is True
    assert service.get_cart(1) is None

def test_clear_cart_only_affects_that_customer(service):
    service.add_item(1, 1, "Grilled Salmon", 1)
    service.add_item(3, 2, "French Toast", 1)
    service.clear_cart(1)
    assert service.get_cart(3) is not None

def test_clear_cart_with_no_cart_returns_false(service):
    assert service.clear_cart(1) is False