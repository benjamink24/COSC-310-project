import pytest
from pydantic import ValidationError
from app.schemas.restaurant import *
from app.schemas.customer import *
from app.schemas.cart import *
from app.schemas.checkout import *

def test_restaurant_model_validity():
    valid_data = {
        "Name": "Waterfront Wines",
        "Cuisine": "Farm-to-Table",
        "Address": "1180 Sunset Dr #104, Kelowna, BC",
        "Hours": "5:00 PM - 10:00 PM",
        "Photos": [],
        "menu": [{"Name": "Grilled Salmon", "Price": 32.00, "Availability": True}],
    }
    model = restaurant_model(**valid_data)
    assert model.Name == "Waterfront Wines"
    assert model.Cuisine == "Farm-to-Table"
    assert len(model.menu) >= 1


def test_restaurant_model_missing_values():
    invalid_data = {"Cuisine": "French", "Address": "456 University Way"}
    with pytest.raises(ValidationError):
        restaurant_model(**invalid_data)


def test_customer_model_validity():
    valid_data = {
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
    model = customer_model(**valid_data)
    assert model.firstName == "Jane"
    assert model.active == True
    assert model.cId == 1

def test_cart_model_validity():
    valid_data = {
        "Cid ": "user_67",
        "items": [
            {"name": "name_1", "quantity": 2, "price": 19.99, "availability": true}
        ]
    }
    model = cart_model(**valid_data)
    assert cart.Cid == "user_67"
    assert len(cart.items) == 1
    assert cart.items[0].quantity == 2

def test_checkout_model_validity():
    valid_data = {
        "Cid": "user_67",
        "email": "jimplingus@gmail.com",
        "shipping_address": {
            "street": "123 Playground st",
            "city": "Farmstrong",
            "postal_code": "V1T 2A2",
        },
        "payment_method": "credit_card",
        "subtotal": 100.00,
        "tax": 12.00,
        "total": 112.00
    }
    model = checkout_model(**valid_data)
    assert checkout.cart_id == "cart_67"
    assert checkout.shipping_address.city == "Farmstrong"
    assert checkout.total == 112.00

def test_restaurant_model_missing_values():
    invalid_data = {"cId": 1 , "Address": "456 University Way"}
    with pytest.raises(ValidationError):
        customer_model(**invalid_data)

def test_external_model_validity():
    valid_data = {
        "orderHistory": [],
        "active": True,
        "cId": 1
    }
    model = external_viewer_model(**valid_data)
    assert model.active == True
    assert model.cId == 1
    assert len(model.orderHistory) == 0