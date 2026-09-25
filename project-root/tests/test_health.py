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
    assert response.json() == rest.get_restaurants()


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
