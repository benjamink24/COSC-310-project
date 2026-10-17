from fastapi import APIRouter, HTTPException
from app.services.restaurant_service import resService
from app.schemas.restaurant import *

router: APIRouter = APIRouter(prefix="/restaurants", tags=["restaurants"])
restaurant: resService = resService()


# 1. GET all restaurants (Working)

@router.get("/",response_model = list[restaurant_name_cuisine_model],summary="Lists restaurants",
    description="Returns the name, cuisine, and ID of all restaurants",
    responses={404: {"model": error_response_model, "description": "Restaurant not found"}})
def list_restaurants():
    restaurant_list = restaurant.get_restaurants()
    return restaurant_list


# 2. CREATE a restaurant (Working)
@router.post("/", response_model=restaurant_model,summary="create a new reastaurant",
    description="Creates a new restaurant in the json file from the provided data which is vetted by the pydantic model", status_code=201)
def create_restaurant(restaurant_data: restaurant_model):
    return restaurant.create_restaurant(restaurant_data.model_dump())


# 3. UPDATE a restaurant (Fixes 405 if missing)
@router.put("/{rest_name}", response_model=restaurant_model,summary="updates a reastaurant",
    description="Updates a restaurant in the json file from the provided data which is vetted by the pydantic model",status_code=201)
def update_restaurant(rest_name: str, update_data: restaurant_model):
    updated = restaurant.update_restaurant(rest_name, update_data.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return updated


# 4. ADD MENU ITEM (Fixes 405 if missing)
@router.post("/{res_name}/menu", response_model=restaurant_model,summary="creates a menu item",
    description="Updates a restaurant in the json file from the provided data which is vetted by the pydantic model",status_code=201)
def add_menu_item(res_name: str, menu_item: menu_model):
    updated = restaurant.add_menu_item(res_name, menu_item.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return updated


@router.put("/{res_name}/menu/{item_name}",summary="Updates a menu item",
    description="Updates a menu item in the json file from the provided data which is vetted by the pydantic model", response_model=restaurant_model)
def update_menu_item(res_name: str, item_name: str, menu_item_update: menu_model):
    updated = restaurant.update_menu_item(
        res_name, item_name, menu_item_update.model_dump()
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Restaurant or menu item not found")
    return updated


@router.get(
    "/{restaurant_name}",
    response_model=restaurant_details_model,
    summary="Get restaurant details",
    description="Returns the name, cuisine, address and hours of one restaurant, looked up by name (case-insensitive).",
    responses={404: {"model": error_response_model, "description": "Restaurant not found"}}
)
def view_restaurant_details(restaurant_name: str):
    result = restaurant.get_restaurants_by_name(restaurant_name)
    if result is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return result


@router.get(
    "/{restaurant_name}/menu",
    response_model=list[menu_model],
    summary="Get a restaurant's menu",
    description="Returns every menu item of the restaurant.",
    responses={404: {"model": error_response_model, "description": "Restaurant not found"}}

)
def view_restaurant_menu(restaurant_name: str):
    result = restaurant.get_restaurants_by_name(restaurant_name)
    if result is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return result.get("menu", [])


@router.get(
    "/{restaurant_name}/menu/{menu_item}",response_model=menu_model,
    summary="Get one menu item",  description="Returns a single menu item of the restaurant, looked up by item name (case-insensitive).",
    responses={ 404: {"model": error_response_model, "description": "Restaurant or menu item not found"}
    }
)
def view_restaurant_menu_item(restaurant_name: str, menu_item: str):
    if restaurant.get_restaurants_by_name(restaurant_name) is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    item = restaurant.get_menu_items(restaurant_name, menu_item)
    if item is None:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return item




@router.get("/filter/{cuisine_type}", response_model= list[restaurant_name_model], summary="filters avalible restaurants by cuisine",  
            description="Returns the name and Id of one restaurants sharing a cuisine type, looked up by cuisine (case-insensitive)",
            responses={ 404: {"model": error_response_model, "description": "Restaurant or menu item not found"}})
def filter_restaurants(cuisine_type: str):
    return restaurant.get_restaurants_by_cuisine_type(cuisine_type)
