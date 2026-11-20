import json
from pathlib import Path


class restaurantOwnerRepo:
    def __init__(self, file_path: str | None = None):
        self.file_path = Path(file_path or "./data/restaurant_owners.json")

    def get_all(self) -> list[dict]:
        if not self.file_path.exists():
            return []
        with self.file_path.open("r", encoding="utf-8") as file:
            data = json.load(file)
        if isinstance(data, list):
            return data
        return data.get("owners", [])

    def get_by_username(self, username: str) -> dict | None:
        normalized_username = username.strip().casefold()
        return next(
            (
                owner
                for owner in self.get_all()
                if owner.get("username", "").strip().casefold()
                == normalized_username
            ),
            None,
        )

    def username_or_email_exists(self, username: str, email: str) -> bool:
        normalized_username = username.strip().casefold()
        normalized_email = email.strip().casefold()
        return any(
            owner.get("username", "").strip().casefold() == normalized_username
            or owner.get("emailAddress", "").strip().casefold() == normalized_email
            for owner in self.get_all()
        )

    def next_id(self) -> int:
        return max((int(owner.get("ownerId", 0)) for owner in self.get_all()), default=0) + 1

    def add_owner(self, owner_data: dict) -> dict:
        owners = self.get_all()
        owners.append(owner_data)
        self.save_all(owners)
        return owner_data

    def save_all(self, owners: list[dict]) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with self.file_path.open("w", encoding="utf-8") as file:
            json.dump(owners, file, indent=4)
