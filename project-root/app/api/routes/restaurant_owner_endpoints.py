from fastapi import APIRouter, Depends, Header, HTTPException, Response

from app.api.dependencies import require_restaurant_owner

from app.schemas.restaurant_owner import (
    restaurant_owner_login_model,
    restaurant_owner_login_response_model,
    restaurant_owner_profile_response_model,
    restaurant_owner_registration_model,
    restaurant_owner_registration_response_model,
)
from app.services.restaurant_owner_service import owner_service

router = APIRouter(prefix="/restaurant-owners", tags=["restaurant owners"])
owner = owner_service


@router.post(
    "/register",
    response_model=restaurant_owner_registration_response_model,
    status_code=201,
    summary="Register a restaurant owner and restaurant",
)
def register_restaurant_owner(owner_data: restaurant_owner_registration_model):
    return owner.create_owner(owner_data.model_dump())


@router.post(
    "/login",
    response_model=restaurant_owner_login_response_model,
    summary="Authenticate a restaurant owner",
)
def login_restaurant_owner(credentials: restaurant_owner_login_model):
    session = owner.authenticate_owner(credentials.username, credentials.password)
    if session is None:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return session


@router.get(
    "/me",
    response_model=restaurant_owner_profile_response_model,
    summary="Get the authenticated owner and restaurant account",
)
def get_restaurant_owner_profile(
    session: dict = Depends(require_restaurant_owner),
):
    profile = owner.get_owner_profile(session["ownerId"])
    if profile is None:
        raise HTTPException(status_code=404, detail="Owner or restaurant not found")
    return profile


@router.post("/logout", status_code=204, summary="End the owner session")
def logout_restaurant_owner(
    authorization: str = Header(...),
    session: dict = Depends(require_restaurant_owner),
):
    _, _, access_token = authorization.partition(" ")
    owner.revoke_session(access_token.strip())
    return Response(status_code=204)
