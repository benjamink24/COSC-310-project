import json
from pathlib import Path
import os
from .repository import AbstractRepository

class histRepo:
    def __init__(self, file_path: str | None = None):
        if file_path is None:
            file_path = "./data/history.json"
         
        self.file_path: Path = Path(file_path)

    def get_all(self) -> list:
        if not self.file_path.exists():
            return []
        with open(self.file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return data.get("orders", [])

    def get_all_orders(self) -> list:
        return self.get_all()

    def add_order(self, order_dict: dict) -> dict:
                orders = self.get_all_orders()
                orders.append(order_dict)
                self.save_all({"orders": orders})
                return order_dict

    def add(self, item_dict: dict) -> dict:
        return self.add_order(item_dict)

    def save_all(self, data):
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)