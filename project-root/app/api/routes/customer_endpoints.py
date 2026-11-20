from fastapi import APIRouter, Depends, Header, HTTPException, Response
from app.services.customer_service import customerService, customer_service
from app.schemas.customer import *
from app.api.dependencies import require_customer_authentication

router: APIRouter = APIRouter(prefix="/customer", tags=["customer"])
customer: customerService = customer_service

#logs in to cusotmmer accoint
@router.post("/login",
             response_model=customer_login_response_model,
             summary="Authenticates a customer account")
def login_customer(credentials: customer_login_model):
    session = customer.authenticate_customer( credentials.username, credentials.password)
    if session is None:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return session


# add customer
@router.post("/", 
             response_model=customer_model,
             summary="create a new customer",
             description="Creates a new customer in the json file from the provided data which is vetted by the pydantic model", status_code=201)
def create_customer(customer_data: add_customer_model):
    return customer.create_customer(customer_data.model_dump())

# @router.get("/",
#             response_model = list[external_viewer_model],
#             summary="Lists customers only external inof avalible", # idea for res owners 
#             description="Returns the name, cuisine, and ID of all restaurants",
#             responses={404: {"model": error_response_model, "description": "Restaurant not found"}})
# def list_customers():
#     customerList = customer.get_customers()
#     return customerList

#get specific customer
@router.get("/me",
            response_model = customer_model,
            summary="provides all of a costomers personal info", # idea for res owners 
            description="Returns the all fileds found in customer_modle for a specific Customer",
            responses={404: {"model": error_response_model, "description": "customer not found"}})
def get_customer(session: dict = Depends(require_customer_authentication),):
    cId = session["cId"]
    individualCustomer = customer.get_customers_by_id(cId)
    if individualCustomer is None:
            raise HTTPException(status_code=404, detail="customer not found")
    return  individualCustomer

@router.put("/me", 
            response_model=customer_model,
            summary="updates a customer",
            description="Updates a customer in the json file from the provided data which is vetted by the pydantic model",status_code=201)
def update_customer(update_data: update_customer_model, session: dict = Depends(require_customer_authentication)):
    cId = session["cId"]
    updated = customer.update_customer(cId, update_data.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail="Customer not found")
    return updated



@router.post("/logout", status_code=204, summary="End the customer session")
def logout_customer(
    authorization: str = Header(...),
    session: dict = Depends(require_customer_authentication),
):
    _, _, access_token = authorization.partition(" ")
    customer.revoke_session(access_token.strip())
    return Response(status_code=204)