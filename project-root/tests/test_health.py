from urllib import response

from fastapi.testclient import TestClient
import json
from app.services.restaurant_service import resService
from app.schemas.restaurant import restaurant_model, menu_model
from app.main import app

rest = resService()
client = TestClient(app)


def test_restaurants():
     response = client.get("/restaurants")
     assert response.status_code == 200
     expected = [{"Name": r["Name"]} for r in rest.get_restaurants()]
     assert response.json() == expected


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
