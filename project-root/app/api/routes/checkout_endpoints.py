from fastapi import APIRouter, HTTPException
from app.services.checkout_service import checkoutService
from app.schemas.checkout import *
from app.schemas.customer import error_response_model

router: APIRouter = APIRouter(prefix="/checkout", tags=["checkout"])
checkout: checkoutService = checkoutService()

@router.post("/",
             response_model=order_model,
             summary="Checks out a cart",
             description="Turns the customer's cart into an order saved in their history, charged at the current menu prices, and then empties the cart",
             responses={400: {"model": error_response_model, "description": "Cart is empty"},
                        404: {"model": error_response_model, "description": "Customer not found"},
                        409: {"model": error_response_model, "description": "An item is no longer available"}},
             status_code=201)
def place_order(request: checkout_request_model):
        return checkout.checkout(request.cId, request.paymentMethod)

@router.get("/history/{cId}",
            response_model = list[order_model],
            summary="Lists a customer's past orders",
            description="Returns every order the customer has placed, oldest first, or an empty list if they have none",
            responses={404: {"model": error_response_model, "description": "Customer not found"}})
def order_history(cId: int):
        return checkout.get_order_history(cId)
