from pydantic import BaseModel
from typing import List


class menu_model(BaseModel):
    Name: str
    Price: float
    Availability: bool


class restaurant_model(BaseModel):
    id: int
    Name: str
    Cuisine: str
    Address: str
    Hours: str
    Photos: list[str] = []
    menu: list[menu_model] = []
