from pydantic import BaseModel, Field
from typing import List

class cart_item_model(BaseModel):
    name: str= Field(min_length=1, max_length=100)
    quantity: int
    price: float = Field(ge=0, le=10000, allow_inf_nan=False)


class cart_model(BaseModel):
    cId: int
    items: List[cart_item_model]


class cart_line_model(BaseModel):
    """One line in a cart or order Name and Price are copied from the restaurant menu."""
    Name: str = Field(min_length=1, max_length=100)
    Price: float = Field(ge=0, le=10000, allow_inf_nan=False)
    quantity: int = Field(gt=0)


class add_cart_item_model(BaseModel):
    """the price comes from the menu"""
    restaurantId: int
    Name: str = Field(min_length=1, max_length=100)
    quantity: int = Field(gt=0)


class update_cart_item_model(BaseModel):
    """Body of PUT /cart/{cId}/items/{item_name}"""
    quantity: int = Field(gt=0)


class cart_view_model(BaseModel):
    """What the cart routes return"""
    cId: int
    restaurantId: int
    items: list[cart_line_model] = []
    total: float
