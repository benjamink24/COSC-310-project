import json
import pytest
from app.repositories.cart_repo import cartRepo

def test_get_all_carts_success(tmp_path):
    """Valid file with cart data loads correctly."""
    data_file = tmp_path / "cart.json"
    data_file.write_text(
        json.dumps(
             {
                "carts": [
                    {
                        "Cid": 1,
                        "items": [{"name": "name_1", "quantity": 2, "price": 12.99}],
                    },
                    {
                        "Cid": 2,
                        "items": [],
                    },
                ]
            }
        )
    )
    repo = cartRepo(file_path=str(data_file))
    result = repo.get_all_carts()

    assert result == [
        {
          "Cid": 1,
          "items": [{"name": "name_1", "quantity": 2, "price": 12.99}],
        },
        {
            "Cid": 2,
            "items": [],
        },
    ]

def test_get_all_carts_empty_list(tmp_path):
    """Valid file with an empty carts list returns an empty list."""
    data_file = tmp_path / "carts.json"
    data_file.write_text(json.dumps({"carts": []}))

    repo = CartRepo(file_path=str(data_file))
    result = repo.get_all_carts()

    assert result == []


def test_get_all_carts_missing_file(tmp_path):
    """Non-existent file handles missing state cleanly."""
    data_file = tmp_path / "does_not_exist.json"

    repo = CartRepo(file_path=str(data_file))
    result = repo.get_all_carts()

    assert result == []