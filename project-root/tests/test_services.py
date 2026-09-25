from app.services.restaurant_service import resService


class mockRepository:
    def get_all_restaurants(self):
        return [
            {
                "id": 1,
                "Name": "Waterfront Wines",
                "Cuisine": "Farm-to-Table",
                "Address": "1180 Sunset Dr #104, Kelowna, BC",
                "Hours": "5:00 PM - 10:00 PM",
                "Photos": [],
                "menu": [
                    {"name": "Grilled Salmon", "price": 32.00, "availability": True}
                ],
            }
        ]


def test_restaurant_services_fetchs_data():
    mock_repo = mockRepository()
    service = resService(repo=mock_repo)
    results = service.get_restaurants()

    assert isinstance(results, list)
    assert len(results) == 1
    assert results[0]["Name"] == "Waterfront Wines"
    assert results[0]["id"] == 1
