import json
from pathlib import Path
import os
from .repository import AbstractRepository

class cartRepo(AbstractRepository):
    def __init__(self, file_path: str | None = None):
        if file_path is None:
            file_path = "./data/cart.json"

        self.file_path: Path = Path(file_path)

    def get_all(self) -> list:
        if not self.file_path.exists():
            return []
        with open(self.file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return data.get("carts", [])

    def get_by_field(self, field: str, value: str) -> list:
        carts = self.get_all()
        filtered = []
        for c in carts:
            if str(field).strip().lower() == "cId":
                if "cId" in r and str(r.get("cId")) == str(value):
                    filtered.append(r)
            else:
                if str(r.get(field, "")).strip().lower() == str(value).strip().lower():
                    filtered.append(r)
        return filtered

    def get_all_carts(self) -> list:
        return self.get_all()

    def update_cart(self, cId, update_data: dict) -> dict:
                carts = self.get_all_carts()
                for c in carts:
                    if "cId" in c and str(c.get("cId")) == str(cId): 
                        c.update(update_data)
                        self.save_all(carts)
                        return c
                return None

    def add_cart(self, cart_dict: dict) -> dict:
                carts = self.get_all_carts()
                if carts and "cId" in carts[-1]:
                    new_id = int(carts[-1]["cId"]) + 1
                else:
                    new_id = 1
                cart_dict["cId"] = new_id
                carts.append(cart_dict)
                self.save_all(carts)
                return cart_dict

    def add(self, item_dict: dict) -> dict:
        return self.add_cart(item_dict)

    def update(self, identifier, update_data: dict) -> dict:
        return self.update_cart(identifier, update_data)

    def get_carts_by_id(self, cId) -> dict:
        results = self.get_by_field("cId", cId)
        return results[0] if results else None

    def save_all(self, data):
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)