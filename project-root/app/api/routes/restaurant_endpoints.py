from fastapi import APIRouter, HTTPException
from app.services.restaurant_service import resService
from app.schemas.restaurant import restaurant_model, menu_model

router: APIRouter = APIRouter()
restaurant: resService = resService()


# 1. GET all restaurants (Working)
@router.get("/restaurants", response_model=list[restaurant_model])
def list_restaurants():
    return restaurant.get_restaurants()


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
