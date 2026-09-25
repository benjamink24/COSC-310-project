import pytest
from pydantic import ValidationError
from app.schemas.restaurant import restaurant_model, menu_model


def test_restaurant_model_validity():
    valid_data = {
        "id": 1,
        "Name": "Waterfront Wines",
        "Cuisine": "Farm-to-Table",
        "Address": "1180 Sunset Dr #104, Kelowna, BC",
        "Hours": "5:00 PM - 10:00 PM",
        "Photos": [],
        "menu": [{"name": "Grilled Salmon", "price": 32.00, "availability": True}],
    }
    model = restaurant_model(**valid_data)
    assert model.id == 1
    assert model.Name == "Waterfront Wines"
    assert model.Cuisine == "Farm-to-Table"
    assert len(model.menu) >= 1


def test_restaurant_model_missing_values():
    invalid_data = {"Cuisine": "French", "Address": "456 University Way"}
    with pytest.raises(ValidationError):
        restaurant_model(**invalid_data)
