from pydantic import BaseModel, Field


class customer_order_model(BaseModel):
    orderHistory: list[dict] = []


class customer_model(BaseModel):
    cId: int 
    firstName: str = Field(min_length=1, max_length=100)
    lastName: str = Field(min_length=1, max_length=100)
    Address: str = Field(min_length=1, max_length=100)
    emailAddress: str = Field(min_length=1, max_length=100)
    paymentMethod: str = Field(min_length=1, max_length=100)
    phoneNumber: str = Field(min_length=1, max_length=100)
    active: bool

class add_customer_model(BaseModel):
    firstName: str = Field(min_length=1, max_length=100)
    lastName: str = Field(min_length=1, max_length=100)
    Address: str = Field(min_length=1, max_length=100)
    emailAddress: str = Field(min_length=1, max_length=100)
    paymentMethod: str = Field(min_length=1, max_length=100)
    phoneNumber: str = Field(min_length=1, max_length=100)

class update_customer_model(BaseModel):
    firstName: str = Field(min_length=1, max_length=100)
    lastName: str = Field(min_length=1, max_length=100)
    Address: str = Field(min_length=1, max_length=100)
    emailAddress: str = Field(min_length=1, max_length=100)
    paymentMethod: str = Field(min_length=1, max_length=100)
    phoneNumber: str = Field(min_length=1, max_length=100)
    active: bool
    


class external_viewer_model(BaseModel):
    cId: int 
    active: bool
    orderHistory: list[dict] = []


class error_response_model(BaseModel):   
    """Error body returned with 404 responses."""
    detail: str



