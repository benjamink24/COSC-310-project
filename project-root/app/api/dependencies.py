from fastapi import Header, HTTPException

from app.services.restaurant_owner_service import owner_service


def require_restaurant_owner(
    authorization: str | None = Header(default=None),
) -> dict:
    if authorization is None:
        raise HTTPException(
            status_code=401,
            detail="Restaurant owner authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    scheme, separator, access_token = authorization.partition(" ")
    if scheme.casefold() != "bearer" or not separator or not access_token.strip():
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    session = owner_service.get_session(access_token.strip())
    if session is None:
        raise HTTPException(
            status_code=401,
            detail="Session is invalid or expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return session
