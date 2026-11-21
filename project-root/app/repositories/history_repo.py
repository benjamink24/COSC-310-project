import json
from pathlib import Path
import os
from .repository import AbstractRepository

class histRepo(AbstractRepository):
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
        """Saves an order and gives it the next orderId (1 for the first order)."""
        orders = self.get_all_orders()
        ids = []
        for o in orders:
            if "orderId" in o:
                try:
                    ids.append(int(o["orderId"]))
                except (TypeError, ValueError):
                    pass
        order = {**order_dict, "orderId": max(ids) + 1 if ids else 1}
        orders.append(order)
        self.save_all({"orders": orders})
        return order


    def add(self, item_dict: dict) -> dict:
        return self.add_order(item_dict)

    def save_all(self, data):
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def get_orders_by_cid(self, cId) -> list:
        """Every order placed by customer cId, oldest first. [] if none."""
        return [o for o in self.get_all_orders() if str(o.get("cId")) == str(cId)]

    def get_order_by_id(self, orderId) -> dict | None:
        for o in self.get_all_orders():
            if str(o.get("orderId")) == str(orderId):
                return o
        return None

    def get_by_field(self, field: str, value: str) -> list:
        target = str(value).strip().lower()
        return [
            o for o in self.get_all_orders()
            if str(o.get(field, "")).strip().lower() == target
        ]
    
    def update(self, identifier, update_data: dict) -> dict | None:
        """Update an order by orderId (e.g. change its status)."""
        orders = self.get_all_orders()
        for o in orders:
            if str(o.get("orderId")) == str(identifier):
                o.update(update_data)
                self.save_all({"orders": orders})
                return o
        return None
