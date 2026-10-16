# from http.client import HTTPException

# import pytest
# from fastapi.testclient import TestClient

# from app.main import app
# from app.api.routes import restaurant_endpoints


# class MockRepo:
#     def get_all_restaurants(self):
#         return [
#             {
#                 "id": 1,
#                 "Name": "Waterfront Wines",
#                 "Cuisine": "Farm-to-Table",
#                 "Address": "1180 Sunset Dr #104, Kelowna, BC",
#                 "Hours": "5:00 PM - 10:00 PM",
#                 "Photos": [],
#                 "menu": [
#                     {"Name": "Grilled Salmon", "Price": 32.0, "Availability": True},
#                     {"Name": "Duck Confit", "Price": 36.0, "Availability": False},
#                 ],
#             }
#         ]


# @pytest.fixture
# def client(monkeypatch):
#     # Swap in fake data so the tests don't depend on restaurants.json
#     monkeypatch.setattr(restaurant_endpoints.restaurant, "repo", MockRepo())
#     return TestClient(app)


# # --- Restaurant details ---

# def test_get_valid_restaurant(client):
#     response = client.get("/restaurants/Waterfront Wines")
#     assert response.status_code == 200
#     assert response.json() == {
#         "Name": "Waterfront Wines",
#         "Cuisine": "Farm-to-Table",
#         "Address": "1180 Sunset Dr #104, Kelowna, BC",
#         "Hours": "5:00 PM - 10:00 PM",
#     }


# def test_restaurant_name_is_case_insensitive(client):
#     assert client.get("/restaurants/waterfront wines").status_code == 200


# def test_get_invalid_restaurant(client):
#     response = client.get("/restaurants/Nonexistent Place")
#     assert response.status_code == 404
#     assert response.json()["detail"] == "Restaurant not found"


# def test_get_valid_menu(client):
#     response = client.get("/restaurants/Waterfront Wines/menu")
#     assert response.status_code == 200
#     body = response.json()
#     assert len(body) == 2
#     assert body[0] == {"Name": "Grilled Salmon", "Price": 32.0, "Availability": True}


# def test_get_menu_invalid_restaurant(client):
#     assert client.get("/restaurants/Nonexistent Place/menu").status_code == 404


# def test_get_valid_menu_item(client):
#     response = client.get("/restaurants/Waterfront Wines/menu/Duck Confit")
#     assert response.status_code == 200
#     assert response.json() == {"Name": "Duck Confit", "Price": 36.0, "Availability": False}


# def test_get_invalid_menu_item(client):
#     response = client.get("/restaurants/Waterfront Wines/menu/Pizza")
#     assert response.status_code == 404
#     assert response.json()["detail"] == "Menu item not found"


# def test_get_menu_item_invalid_restaurant(client):
#     response = client.get("/restaurants/Nonexistent Place/menu/Duck Confit")
#     assert response.status_code == 404
#     assert response.json()["detail"] == "Restaurant not found"