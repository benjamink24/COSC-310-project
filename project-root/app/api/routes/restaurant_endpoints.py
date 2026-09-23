from fastapi import APIRouter
from app.services.restaurant_service import resService
from app.schemas.restaurant import restaurant_model

router: APIRouter = APIRouter()# i can add a prefix to the APIrouter as an arg to make all responses about restaurants.
restaurant: resService = resService()

@router.get("/restaurant",response_model = list[restaurant_model])
def list_restaurants():
    return restaurant.get_restaurants
