from pydantic import BaseModel, Field, field_validator
from typing import List


class menu_model(BaseModel):
    Name: str  = Field(min_length=1, max_length=100)
    Price: float = Field(ge=0, le=10000, allow_inf_nan=False)
    Availability: bool

    @field_validator("Name")
    @classmethod
    def reject_blank_name(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Menu item name must not be blank")
        return value.strip()


class restaurant_model(BaseModel):
    Name: str = Field(min_length=1, max_length=100)
    Cuisine: str = Field(min_length=1, max_length=100)
    Address: str = Field(min_length=1, max_length=100)
    Hours: str = Field(min_length=1, max_length=100)
    Photos: list[str] = Field(default_factory=list, max_length=20)
    menu: list[menu_model] = Field(default_factory=list)

    @field_validator("Name", "Cuisine", "Address", "Hours")
    @classmethod
    def reject_blank_details(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Restaurant information must not be blank")
        return value.strip()



class restaurant_name_cuisine_model(BaseModel):
     Name: str
     Cuisine: str
     id: int

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