import json
import pytest
from app.repositories.history_repo import histRepo

def test_get_all_orders_success(tmp_path):
    """Valid file with order history data loads correctly."""
    data_file = tmp_path / "order_history.json"
    data_file.write_text(
        json.dumps(
            {
                "orders": [
                    {
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
                        "total": 112.00,
                    },
                    {
                        "Cid": "user_76",
                        "email": "craigbertfinger@icloud.com",
                        "shipping_address": {
                            "street": "456 Oak Ave",
                            "city": "Vernon",
                            "postal_code": "V1T 3B3",
                        },
                        "payment_method": "debit_card",
                        "subtotal": 50.00,
                        "tax": 6.00,
                        "total": 56.00,
                    },
                ]
            }
        )
    )
    repo = histRepo(file_path=str(data_file))
    result = repo.get_all_orders()

    assert result == [
        {
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
            "total": 112.00,
            },
            {
            "Cid": "user_76",
            "email": "craigbertfinger@icloud.com",
            "shipping_address": {
                "street": "456 Oak Ave",
                "city": "Vernon",
                "postal_code": "V1T 3B3",
            },
            "payment_method": "debit_card",
            "subtotal": 50.00,
            "tax": 6.00,
            "total": 56.00,
            },
    ]
