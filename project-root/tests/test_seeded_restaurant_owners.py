import json
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def test_named_restaurants_have_linked_owner_accounts():
    with (DATA_DIR / "restaurants.json").open(encoding="utf-8") as file:
        restaurants = json.load(file)
    with (DATA_DIR / "restaurant_owners.json").open(encoding="utf-8") as file:
        owners = json.load(file)

    owners_by_id = {owner["ownerId"]: owner for owner in owners}
    named_restaurants = [
        restaurant
        for restaurant in restaurants
        if restaurant.get("Name", "").strip().casefold() != "string"
    ]

    assert named_restaurants
    for restaurant in named_restaurants:
        owner = owners_by_id[restaurant["ownerId"]]
        assert owner["restaurantId"] == restaurant["id"]
        assert owner["firstName"]
        assert owner["lastName"]
        assert owner["Address"]
        assert owner["username"]
        assert owner["passwordHash"]
        assert "password" not in owner
        assert "demoAccount" not in owner
