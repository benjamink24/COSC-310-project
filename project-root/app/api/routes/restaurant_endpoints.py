from fastapi import APIRouter, HTTPException
from app.services.restaurant_service import resService
from app.schemas.restaurant import *


router: APIRouter = APIRouter(prefix="/restaurants", tags=["restaurants"])# i can add a prefix to the APIrouter as an arg to make all responses about restaurants.
restaurant: resService = resService()



# 1. GET all restaurants (Working)
@router.get("/",response_model = list[restaurant_name_model])
def list_restaurants():
    """
    returns a list of restaurant names


    """
    restaurant_list= restaurant.get_restaurants()
    return restaurant_list


# 2. CREATE a restaurant (Working)
@router.post("/restaurants", response_model=restaurant_model, status_code=201)
def create_restaurant(restaurant_data: restaurant_model):
    return restaurant.create_restaurant(restaurant_data.model_dump())


# 3. UPDATE a restaurant (Fixes 405 if missing)
@router.put("/restaurants/{rest_id}", response_model=restaurant_model)
def update_restaurant(rest_id: int, update_data: restaurant_model):
    updated = restaurant.update_restaurant(rest_id, update_data.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return updated


# 4. ADD MENU ITEM (Fixes 405 if missing)
@router.post("/restaurants/{rest_id}/menu", response_model=restaurant_model)
def add_menu_item(rest_id: int, menu_item: menu_model):
    updated = restaurant.add_menu_item(rest_id, menu_item.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return updated


@router.put("/restaurants/{rest_id}/menu/{item_name}", response_model=restaurant_model)
def update_menu_item(rest_id: int, item_name: str, menu_item_update: menu_model):
    updated = restaurant.update_menu_item(
        rest_id, item_name, menu_item_update.model_dump()
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Restaurant or menu item not found")
    return updated



@router.get(
    "/{restaurant_id}",
    response_model=restaurant_details_model,
    summary="Get restaurant details",
    description="Returns the name, cuisine, address, hours and photos of one restaurant.",
    responses={404: {"model": error_response_model, "description": "Restaurant not found"}},
)
def view_restaurant_details(restaurant_id: int):
    result = restaurant.get_restaurant_by_id(restaurant_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return result


@router.get(
    "/{restaurant_id}/menu",
    response_model=menu_response_model,
    summary="Get a restaurant's menu",
    description="Returns every menu item of the restaurant, each with its item id.",
    responses={404: {"model": error_response_model, "description": "Restaurant not found"}},
)
def view_restaurant_menu(restaurant_id: int):
    result = restaurant.get_menu_by_restaurant_id(restaurant_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return result


@router.get(
    "/{restaurant_id}/menu/{item_id}",
    response_model=menu_item_model,
    summary="Get one menu item",
    description="Returns a single menu item identified by its id within the restaurant's menu.",
    responses={
        404: {"model": error_response_model, "description": "Restaurant or menu item not found"}
    },
)
def view_restaurant_menu_item(restaurant_id: int, item_id: int):
    if restaurant.get_restaurant_by_id(restaurant_id) is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    item = restaurant.get_menu_item_by_id(restaurant_id, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return item
    

@router.get("/filter/{cuisine_type}", response_model= list[restaurant_name_model])
def filter_restaurants(cuisine_type: str):
    return restaurant.get_restaurants_by_cuisine_type(cuisine_type)
    

