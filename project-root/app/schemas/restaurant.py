from pydantic import BaseModel
from typing import List

class restaurant_model(BaseModel):
    id:int
    Name:str
    Cuisine:str
    Address:str
    Hours:str
    Photos: list[Str] = [] #is the list arg supposed to be Str or str?
    menu: list[dict] = []
    