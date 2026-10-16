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


class restaurant_name_model(BaseModel):
     Name: str
     id: int

class restaurant_details_model(BaseModel):
    """Restaurant details: name, cuisine, address and hours only."""    
    Name: str
    Cuisine: str
    Address: str
    Hours: str

class error_response_model(BaseModel):   
    """Error body returned with 404 responses."""
    detail: str