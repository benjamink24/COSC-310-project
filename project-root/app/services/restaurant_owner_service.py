import hashlib
import hmac
import secrets
import threading
import time

from fastapi import HTTPException

from app.repositories.restaurant_owner_repo import restaurantOwnerRepo
from app.repositories.restaurant_repo import resRepo

PASSWORD_HASH_ITERATIONS = 310_000
SESSION_TTL_SECONDS = 3600


class restaurantOwnerService:
    def __init__(
        self,
        repo: restaurantOwnerRepo | None = None,
        restaurant_repo: resRepo | None = None,
    ):
        self.repo = repo or restaurantOwnerRepo()
        self.restaurant_repo = restaurant_repo or resRepo()
        self._sessions: dict[str, dict] = {}
        self._sessions_lock = threading.Lock()

    def create_owner(self, owner_data: dict) -> dict:
        username = owner_data["username"].strip()
        email = str(owner_data["emailAddress"]).strip()
        if self.repo.username_or_email_exists(username, email):
            raise HTTPException(
                status_code=409,
                detail="Username or email is already registered",
            )

        owner_id = self.repo.next_id()
        restaurant_data = dict(owner_data["restaurant"])
        restaurant_data["ownerId"] = owner_id
        restaurant = self.restaurant_repo.add_restaurants(restaurant_data)

        owner = {
            "ownerId": owner_id,
            "active": True,
            "firstName": owner_data["firstName"].strip(),
            "lastName": owner_data["lastName"].strip(),
            "Address": owner_data["Address"].strip(),
            "emailAddress": email,
            "phoneNumber": owner_data["phoneNumber"].strip(),
            "username": username,
            "passwordHash": self._hash_password(owner_data["password"]),
            "restaurantId": restaurant["id"],
        }
        self.repo.add_owner(owner)
        return {
            "ownerId": owner_id,
            "username": username,
            "restaurantId": restaurant["id"],
            "restaurant": restaurant,
        }

    def authenticate_owner(self, username: str, password: str) -> dict | None:
        owner = self.repo.get_by_username(username)
        if (
            owner is None
            or owner.get("active", True) is False
            or not self._verify_password(
            password, owner.get("passwordHash", "")
            )
        ):
            return None
        access_token = secrets.token_urlsafe(32)
        expires_at = time.time() + SESSION_TTL_SECONDS
        session = {
            "username": owner["username"],
            "role": "restaurant",
            "ownerId": owner["ownerId"],
            "restaurantId": owner["restaurantId"],
            "expiresAt": expires_at,
        }
        with self._sessions_lock:
            self._remove_expired_sessions(time.time())
            self._sessions[self._token_key(access_token)] = session
        return {
            **{key: session[key] for key in ("username", "role", "ownerId", "restaurantId")},
            "accessToken": access_token,
            "tokenType": "bearer",
            "expiresIn": SESSION_TTL_SECONDS,
        }

    def get_session(self, access_token: str) -> dict | None:
        now = time.time()
        token_key = self._token_key(access_token)
        with self._sessions_lock:
            self._remove_expired_sessions(now)
            session = self._sessions.get(token_key)
            if session is None:
                return None
            owner = self.repo.get_by_id(session["ownerId"])
            if owner is None or owner.get("active", True) is False:
                del self._sessions[token_key]
                return None
            return {key: value for key, value in session.items() if key != "expiresAt"}

    def revoke_session(self, access_token: str) -> None:
        with self._sessions_lock:
            self._sessions.pop(self._token_key(access_token), None)

    def deactivate_owner(self, owner_id: int) -> None:
        account = self.repo.get_by_id(owner_id)
        if account is None or account.get("active", True) is False:
            raise HTTPException(status_code=404, detail="Active owner account not found")

        restaurant = self.restaurant_repo.get_restaurants_by_id(
            account["restaurantId"],
            include_inactive=True,
        )
        if restaurant is None:
            raise HTTPException(status_code=404, detail="Restaurant not found")

        updated_owner = self.repo.update_owner(owner_id, {"active": False})
        if updated_owner is None:
            raise HTTPException(status_code=404, detail="Owner account not found")
        updated_restaurant = self.restaurant_repo.update_res(
            account["restaurantId"], {"active": False}
        )
        if updated_restaurant is None:
            raise HTTPException(status_code=404, detail="Restaurant not found")

        with self._sessions_lock:
            owner_tokens = [
                token_key
                for token_key, session in self._sessions.items()
                if str(session["ownerId"]) == str(owner_id)
            ]
            for token_key in owner_tokens:
                del self._sessions[token_key]

    def get_owner_profile(self, owner_id: int) -> dict | None:
        account = next(
            (
                owner
                for owner in self.repo.get_all()
                if int(owner.get("ownerId", -1)) == owner_id
            ),
            None,
        )
        if account is None:
            return None
        restaurant = self.restaurant_repo.get_restaurants_by_id(
            account["restaurantId"]
        )
        if restaurant is None:
            return None
        return {
            "ownerId": account["ownerId"],
            "firstName": account["firstName"],
            "lastName": account["lastName"],
            "Address": account["Address"],
            "emailAddress": account["emailAddress"],
            "phoneNumber": account["phoneNumber"],
            "username": account["username"],
            "restaurantId": account["restaurantId"],
            "restaurant": restaurant,
        }

    @staticmethod
    def _hash_password(password: str) -> str:
        salt = secrets.token_bytes(16)
        password_hash = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt, PASSWORD_HASH_ITERATIONS
        )
        return (
            f"pbkdf2_sha256${PASSWORD_HASH_ITERATIONS}"
            f"${salt.hex()}${password_hash.hex()}"
        )

    @staticmethod
    def _verify_password(password: str, stored_hash: str) -> bool:
        try:
            algorithm, iterations, salt_hex, expected_hash_hex = stored_hash.split("$", 3)
            if algorithm != "pbkdf2_sha256" or int(iterations) != PASSWORD_HASH_ITERATIONS:
                return False
            salt = bytes.fromhex(salt_hex)
            expected_hash = bytes.fromhex(expected_hash_hex)
        except (AttributeError, ValueError):
            return False
        actual_hash = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt, PASSWORD_HASH_ITERATIONS
        )
        return hmac.compare_digest(actual_hash, expected_hash)

    @staticmethod
    def _token_key(access_token: str) -> str:
        return hashlib.sha256(access_token.encode("utf-8")).hexdigest()

    def _remove_expired_sessions(self, now: float) -> None:
        expired = [
            token_key
            for token_key, session in self._sessions.items()
            if session["expiresAt"] <= now
        ]
        for token_key in expired:
            del self._sessions[token_key]


owner_service = restaurantOwnerService()
