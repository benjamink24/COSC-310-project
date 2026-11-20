import hashlib
import hmac
import secrets
import threading
import time

from app.repositories.customer_repo import customerRepo
from app.email_validation import is_valid_email
from app.bloom import UsernameBloomFilter as bloom
from fastapi import HTTPException

PASSWORD_HASH_ITERATIONS = 310_000
SESSION_TTL_SECONDS = 3600

class customerService:
    def __init__(self, repo: customerRepo = customerRepo(), bloom_filter: bloom = bloom(1000, 0.01)):
        self.repo = repo
        self.bloom_filter = bloom_filter
        for customer in self.repo.get_all_customers():
            self.bloom_filter.add(customer["username"])
               
        self._sessions: dict[str, dict] = {}
        self._sessions_lock = threading.Lock()

    def get_customers(self) -> list:
        return self.repo.get_all_customers()


    def create_customer(self, customer_data: dict) -> dict: # needs to be valid email needs to be accepted payment method, needs to be unqiue username. must be valid names 
        customerService.check_required_feilds(customer_data)
        customerService.accepted_payment_method(customer_data.get("paymentMethod"))
        customerService.validate_email(customer_data.get("emailAddress"))
        customerService.validate_password(customer_data.get("password"))
        customerService.validate_username(self, customer_data.get("username"))
        customer_data["password"] = self._hash_password(customer_data["password"])
        self.bloom_filter.add(customer_data.get("username"))
        return self.repo.add_customer(customer_data)

    def update_customer(self, cId: int, update_data: dict):
        customerService.check_required_feilds(update_data)
        customerService.accepted_payment_method(update_data.get("paymentMethod"))
        customerService.validate_email(update_data.get("emailAddress"))
        customerService.validate_password(update_data.get("password"))
        customerService.validate_username(self, update_data.get("username"))
        update_data["password"] = self._hash_password(update_data["password"])
        return self.repo.update_customer(cId, update_data)

    def get_customers_by_id(self, cId: int) -> list:
        return self.repo.get_customers_by_id(cId)

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


    def authenticate_customer(self, username: str, password: str) -> dict | None:
            customer = self.repo.get_by_field("username", username)
            customer= customer[0] if customer else None
            if customer is None or not self._verify_password(
                password, customer.get("password", "")
            ):
                return None
            access_token = secrets.token_urlsafe(32)
            expires_at = time.time() + SESSION_TTL_SECONDS
            session = {
                "username": customer["username"],
                "role": "customer",
                "cId": customer["cId"],
                "expiresAt": expires_at,
            }
            with self._sessions_lock:
                self._remove_expired_sessions(time.time())
                self._sessions[self._token_key(access_token)] = session
            return {
                **{key: session[key] for key in ("username", "role", "cId")},
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
            return {key: value for key, value in session.items() if key != "expiresAt"}

    def revoke_session(self, access_token: str) -> None:
        with self._sessions_lock:
            self._sessions.pop(self._token_key(access_token), None)

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
    def validate_email(email : str):
        if not is_valid_email(email):
            raise HTTPException(status_code=422, detail="Unacceptable email")

    @staticmethod
    def check_required_feilds(customer: dict):
        required_fields = ["Address","emailAddress","paymentMethod","phoneNumber","username", "password"]
        if any(not customer.get(field) for field in required_fields): # 
            raise HTTPException(status_code=422, detail="missing required fields")# unprocessable as the required feilds are needed send back to front end and re promt


    @staticmethod
    def accepted_payment_method(payment_method:str):
        accepted_payment_methods = ["credit","debit"]
        if any(payment_method.lower()== accepted_payment.lower() for accepted_payment in accepted_payment_methods):
            return
        raise HTTPException(status_code=422, detail="Unacceptable payment method")


    @staticmethod
    def validate_password(password: str):
        if len(password) <= 5 or password.lower() == password:
            raise HTTPException(status_code=422, detail="Unacceptable password ensure it is longer than 5 charicters and has at least 1 uppercase letter")
    
    def validate_username(self, username: str):
        if self.bloom_filter.might_exist(username):
            raise HTTPException(status_code=422, detail="Username is already taken")

customer_service = customerService()