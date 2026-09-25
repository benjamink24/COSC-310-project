import json
import pytest
from repositories.restaurant_repo import resRepo

def test_get_all_restaurants_success(tmp_path):
    """Valid file with restaurant data loads correctly."""
    data_file = tmp_path / "restaurants.json"
    data_file.write_text(json.dumps({
        "restaurants": [
            {"id": 1, "name": "Pasta Place"},
            {"id": 2, "name": "Burger Barn"}
        ]
    }))

    repo = resRepo(file_path=str(data_file))
    result = repo.get_all_restaurants()

    assert result == [
        {"id": 1, "name": "Pasta Place"},
        {"id": 2, "name": "Burger Barn"}
    ]


def test_get_all_restaurants_malformed_json(tmp_path):
    """Invalid/corrupted JSON should raise a JSONDecodeError (failure case)."""
    bad_file = tmp_path / "restaurants.json"
    bad_file.write_text("{ this is not valid json ")

    repo = resRepo(file_path=str(bad_file))

    with pytest.raises(json.JSONDecodeError):
        repo.get_all_restaurants()