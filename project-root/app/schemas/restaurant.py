from pydantic import BaseModel
from typing import List

class restaurant(BaseModel):
    id:int
    Name:str
    Cuisine:str
    Address:str
    Hours:str
    Photos: list[Str] = []
    