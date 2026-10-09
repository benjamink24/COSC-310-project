from fastapi import APIRouter
from app.services.restaurant_service import resService
from app.schemas.restaurant import *

router: APIRouter = APIRouter(prefix="/restaurants", tags=["restaurants"])# i can add a prefix to the APIrouter as an arg to make all responses about restaurants.
restaurant: resService = resService()

@router.get("/",response_model = list[restaurant_name_model])
def list_restaurants():
    """
    returns a list of restaurant names


    """
    restaurant_list= restaurant.get_restaurants()
    return restaurant_list

@router.get("/{restaurant_name}", response_model=restaurant_model)
def view_restaurant_details(restaurant_name : str):# create a method that returns a restraughnts deatials by name as key
    return restaurant.get_restaurants_by_name(restaurant_name)

@router.get("/{restaurant_name}/menu", response_model= list[menu_model])
def view_restaurant_menu(restaurant_name : str):
    restaurant_details=restaurant.get_restaurants_by_name(restaurant_name)
    return restaurant_details["menu"]

@router.get("/{restaurant_name}/menu/{menu_item}", response_model= menu_model)
def view_restaurant_menu_item(restaurant_name : str, menu_item: str):
    return restaurant.get_menu_items(restaurant_name,menu_item)
    

@router.get("/filter/{cuisine_type}", response_model= list[restaurant_name_model])
def filter_restaurants(cuisine_type: str):
    return restaurant.get_restaurants_by_cuisine_type(cuisine_type)
    