from pydantic import BaseModel
from typing import List

class restaurant_model(BaseModel):
    id:int
    Name:str
    Cuisine:str
    Address:str
    Hours:str
    Photos: list[str] = [] #is the list arg supposed to be Str or str?
    menu: list[menu_model] = []

class menu_model(BaseModel):
    name : str
    price: float
    availability: bool
    