from pydantic import BaseModel, Field

class shipping_address_model(BaseModel):
    street: str = Field(min_length=1, max_length=100)
    city: str = Field(min_length=1, max_length=100)
    postal_code: str= Field(min_length=5, max_length=10)

class checkout_model(BaseModel):
    cId: int
    emailAddress: str = Field(min_length=1, max_length=100)
    shippingAddress: shipping_address_model
    paymentMethod: str = Field(min_length=1, max_length=100)
    subtotal: float = Field(ge=0, le=10000, allow_inf_nan=False)
    tax: float = Field(ge=0, le=10000, allow_inf_nan=False)
    total: float = Field(ge=0, le=10000, allow_inf_nan=False)

