from pydantic import BaseModel, Field
from typing import List

class cart_item_model(BaseModel):
    name: str= Field(min_length=1, max_length=100)
    quantity: int
    price: float = Field(ge=0, le=10000, allow_inf_nan=False)


class cart_model(BaseModel):
    cId: int
    items: List[cart_item_model]