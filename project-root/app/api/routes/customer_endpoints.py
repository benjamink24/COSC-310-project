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
            raise HTTPException(status_code=404, detail="customer not found")
    return  individualCustomer
#add customer
@router.post("/", 
             response_model=customer_model,
             summary="create a new customer",
             description="Creates a new customer in the json file from the provided data which is vetted by the pydantic model", status_code=201)
def create_restaurant(customer_data: add_customer_model):
    return customer.create_customer(customer_data.model_dump())


# 3. UPDATE a customer (Fixes 405 if missing)
@router.put("/{cId}", 
            response_model=customer_model,
            summary="updates a customer",
            description="Updates a restaurant in the json file from the provided data which is vetted by the pydantic model",status_code=201)
def update_restaurant(cId: int, update_data: update_customer_model):
    updated = customer.update_customer(cId, update_data.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return updated