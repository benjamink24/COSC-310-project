from pydantic import BaseModel, Field, field_validator

from app.email_validation import is_valid_email
from app.schemas.restaurant import (
    menu_model,
    restaurant_details_model,
)


class restaurant_owner_restaurant_model(BaseModel):
    Name: str = Field(min_length=1, max_length=100)
    Cuisine: str = Field(min_length=1, max_length=100)
    Address: str = Field(min_length=1, max_length=100)
    Hours: str = Field(min_length=1, max_length=100)
    Photos: list[str] = Field(default_factory=list, max_length=20)
    menu: list[menu_model] = Field(default_factory=list)

    @field_validator("Name", "Cuisine", "Address", "Hours")
    @classmethod
    def reject_blank_values(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("This field must not be blank")
        return value.strip()


class restaurant_owner_registration_model(BaseModel):
    firstName: str = Field(min_length=1, max_length=100)
    lastName: str = Field(min_length=1, max_length=100)
    Address: str = Field(min_length=1, max_length=100)
    emailAddress: str = Field(min_length=1, max_length=254)
    phoneNumber: str = Field(min_length=1, max_length=100)
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=8, max_length=100)
    restaurant: restaurant_owner_restaurant_model

    @field_validator("username", "firstName", "lastName", "Address", "phoneNumber")
    @classmethod
    def reject_blank_values(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("This field must not be blank")
        return value.strip()

    @field_validator("emailAddress")
    @classmethod
    def validate_email_address(cls, value: str) -> str:
        value = value.strip()
        if not is_valid_email(value):
            raise ValueError("Invalid email address")
        return value


class restaurant_owner_login_model(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


class restaurant_owner_registration_response_model(BaseModel):
    ownerId: int
    username: str
    restaurantId: int
    restaurant: restaurant_details_model


class restaurant_owner_login_response_model(BaseModel):
    username: str
    role: str
    ownerId: int
    restaurantId: int
    accessToken: str
    tokenType: str
    expiresIn: int


class restaurant_owner_profile_response_model(BaseModel):
    ownerId: int
    firstName: str
    lastName: str
    Address: str
    emailAddress: str
    phoneNumber: str
    username: str
    restaurantId: int
    restaurant: restaurant_owner_restaurant_model
