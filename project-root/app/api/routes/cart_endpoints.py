from fastapi import APIRouter, HTTPException, Response
from app.services.cart_service import cartService
from app.schemas.cart import *
from app.schemas.customer import error_response_model

router: APIRouter = APIRouter(prefix="/cart", tags=["cart"])
cart: cartService = cartService()


# 1. GET a customer's cart
@router.get("/{cId}",
            response_model = cart_view_model,
            summary="Get a customer's cart",
            description="Returns the customer's cart with a computed total",
            responses={404: {"model": error_response_model, "description": "Customer or cart not found"}})
def view_cart(cId: int):
    result = cart.get_cart(cId)
    if result is None:
        raise HTTPException(status_code=404, detail="cart not found")
    return result

@router.post("/{cId}/items",
             response_model=cart_view_model,
             summary="Adds an item to a cart",
             description="Adds a menu item to the cart, the price is read from the restaurant's menu. Adding the same item again increases its quantity and a cart can only hold items from one restaurant",
             responses={404: {"model": error_response_model, "description": "Customer, restaurant or menu item not found"},
                        409: {"model": error_response_model, "description": "Item unavailable or from a different restaurant"}},
             status_code=201)
def add_item(cId: int, item: add_cart_item_model):
        return cart.add_item(cId, **item.model_dump())
    
@router.put("/{cId}/items/{item_name}",
            response_model=cart_view_model,
            summary="Sets the quantity of a cart item",
            description="Replaces the quantity of an item that is already in the cart",
            responses={404: {"model": error_response_model, "description": "Cart or item not found"}})
def update_item(cId: int, item_name: str, update_data: update_cart_item_model):
        return cart.update_item(cId, item_name, update_data.quantity)

@router.delete("/{cId}/items/{item_name}",
               response_model=cart_view_model,
               summary="Removes an item from a cart",
               description="Removes one item from the cart, removing the last item leaves an empty cart",
               responses={404: {"model": error_response_model, "description": "Cart or item not found"}})
def remove_item(cId: int, item_name: str):
        return cart.remove_item(cId, item_name)

@router.delete("/{cId}",
               summary="Deletes a cart",
               description="Deletes the customer's whole cart",
               responses={404: {"model": error_response_model, "description": "Cart not found"}},
               status_code=204)
def clear_cart(cId: int):
    if not cart.clear_cart(cId):
        raise HTTPException(status_code=404, detail="cart not found")
    return Response(status_code=204)