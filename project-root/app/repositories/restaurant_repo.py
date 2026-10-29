import json
from pathlib import Path
from .repository import AbstractRepository


class resRepo(AbstractRepository):

    def __init__(self, file_path: str = "./data/restaurants.json"):
        self.file_path: Path = Path(file_path)

    def get_all(self) -> list:
        if not self.file_path.exists():
            return []
        with open(self.file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return data.get("restaurants", [])

    def get_by_field(self, field: str, value: str) -> list:
        restaurants = self.get_all()
        filtered = []
        for r in restaurants:
            if str(field).strip().lower() == "id":
                if "id" in r and str(r.get("id")) == str(value):
                    filtered.append(r)
            else:
                if str(r.get(field, "")).strip().lower() == str(value).strip().lower():
                    filtered.append(r)
        return filtered

    def add(self, item_dict: dict) -> dict:
        return self.add_restaurants(item_dict)

    def update(self, identifier, update_data: dict) -> dict:
        return self.update_res(identifier, update_data)

    def get_all_restaurants(self) -> list:
        return self.get_all()

    def get_restaurants_by_id(self, restaurant_id) -> dict:
        results = self.get_by_field("id", restaurant_id)
        return results[0] if results else None

    def get_restaurants_by_cuisine_type(self, cuisine_type: str) -> list:
        return self.get_by_field("Cuisine", cuisine_type)

    def save_all(self, data):
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def add_restaurants(self, res_dict: dict) -> dict:
        restaurants = self.get_all_restaurants()
        if "id" not in res_dict or res_dict["id"] is None:
            if restaurants and "id" in restaurants[-1]:
                new_id = int(restaurants[-1]["id"]) + 1
            else:
                new_id = 1
            res_dict["id"] = new_id
        restaurants.append(res_dict)
        self.save_all(restaurants)
        return res_dict

    def update_res(self, restaurant_id, update_data: dict) -> dict:
        restaurants = self.get_all_restaurants()
        for r in restaurants:
            if "id" in r and str(r.get("id")) == str(restaurant_id):
                r.update(update_data)
                self.save_all(restaurants)
                return r
        return None

    def get_menu_items(self, restaurant_id, menu_item_name: str) -> dict:
        restaurant = self.get_restaurants_by_id(restaurant_id)
        if not restaurant:
            return None
        for j in restaurant.get("menu", []):
            if (
                str(j.get("Name", "")).strip().lower()
                == str(menu_item_name).strip().lower()
            ):
                return j
        return None

    def add_menu_item(self, restaurant_id, menu_item_dict: dict) -> dict:
        restaurants = self.get_all_restaurants()
        for r in restaurants:
            if "id" in r and str(r.get("id")) == str(restaurant_id):
                if "menu" not in r or r["menu"] is None:
                    r["menu"] = []
                r["menu"].append(menu_item_dict)
                self.save_all(restaurants)
                return r
        return None

    def update_menu_item(
        self, restaurant_id, item_name: str, update_data: dict
    ) -> dict:
        restaurants = self.get_all_restaurants()
        for r in restaurants:
            if "id" in r and str(r.get("id")) == str(restaurant_id):
                menu = r.get("menu") or []
                for item in menu:
                    if (
                        str(item.get("Name", "")).strip().lower()
                        == str(item_name).strip().lower()
                    ):
                        item.update(update_data)
                        self.save_all(restaurants)
                        return r
        return None
