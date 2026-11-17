from pydantic import BaseModel, Field
from app.schemas.cart import cart_line_model

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

class checkout_request_model(BaseModel):
    """Body of POST /checkout/"""
    cId: int
    paymentMethod: str = Field(min_length=1, max_length=100)


class order_model(BaseModel):
    """entry of history.json"""
    orderId: int
    cId: int
    restaurantId: int
    items: list[cart_line_model] = Field(min_length=1)
    total: float = Field(ge=0, allow_inf_nan=False)
    paymentMethod: str
    status: str = "placed"
    timestamp: str
 