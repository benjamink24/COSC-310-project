from pydantic import BaseModel
from typing import List


class menu_model(BaseModel):
    Name: str
    Price: float
    Availability: bool


class restaurant_model(BaseModel):
    #id: int
    Name: str
    Cuisine: str
    Address: str
    Hours: str
    Photos: list[str] = []
    menu: list[menu_model] = [] 


class restaurant_name_model(BaseModel):
     Name: str

class menu_item_model(BaseModel):
    #A single menu item. id is its 1-based position within the restaurant's menu.
    id: int
    Name: str
    Price: float
    Availability: bool


class menu_response_model(BaseModel):
    #"""The full menu of one restaurant."""
    restaurant_id: int
    restaurant_name: str
    items: list[menu_item_model]


class restaurant_details_model(BaseModel):
    #Restaurant details: name, cuisine, address and hours 
    Name: str
    Cuisine: str
    Address: str
    Hours: str

class error_response_model(BaseModel):
    detail: str