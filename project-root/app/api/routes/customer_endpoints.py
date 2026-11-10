from fastapi import APIRouter, HTTPException
from app.services.customer_service import customerService
from app.schemas.customer import *

router: APIRouter = APIRouter(prefix="/customer", tags=["customer"])
customer: customerService = customerService()

@router.get("/",
            response_model = list[external_viewer_model],
            summary="Lists customers only external inof avalible", # idea for res owners 
            description="Returns the name, cuisine, and ID of all restaurants",
            responses={404: {"model": error_response_model, "description": "Restaurant not found"}})
def list_customers():
    customerList = customer.get_customers()
    return customerList


@router.get("/{cId}",
            response_model = customer_model,
            summary="provides all of a costomers personal info", # idea for res owners 
            description="Returns the name, cuisine, and ID of all restaurants",
            responses={404: {"model": error_response_model, "description": "customer not found"}})
def list_customers(cId: int):
    individualCustomer = customer.get_customers_by_id(cId)
    if individualCustomer is None:
            raise HTTPException(status_code=404, detail="Restaurant not found")
    return  individualCustomer