import json
from pathlib import Path
import os

def running_tests() -> bool:
    return os.environ.get("RUNNING_TESTS") == "1"


class resRepo:
    def __init__(self, file_path: str | None = None):
        if file_path is None:
            file_path = "./data/test.json" if running_tests() else "./data/restaurants.json"
        self.file_path: Path = Path(file_path)

    def get_all_restaurants(self) -> list:
        if not self.file_path.exists():
            return []
        with open(self.file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # If the file is a list, return it directly without .get()
            if isinstance(data, list):
                return data
            return data.get("restaurants", [])

    ####
    def get_restaurants_by_name(self, restaurant_name: str) -> list:
        restaurats_list = self.get_all_restaurants()
        for i in restaurats_list:
            if i["Name"].lower() == restaurant_name.strip().lower():
                return i

        return None

    def get_restaurants_by_id(self, restaurant_id: int):
        for r in self.get_all_restaurants():
            if r["id"] == restaurant_id:
                return r
        return None

    def get_menu_items(self, restaurant_id: int, menu_item: str):
        for r in self.get_all_restaurants():
            if r["id"] == restaurant_id:
                for item in r["menu"]:
                    if item["Name"].lower() == menu_item.lower():
                        return item
        return None

    def get_restaurants_by_cuisine_type(self, cuisine_type: str) -> list:
        restaurats_list = self.get_all_restaurants()
        filtered_restaurants = []
        for i in restaurats_list:
            if i["Cuisine"].lower() == cuisine_type.lower():
                filtered_restaurants.append(i)
        return filtered_restaurants

    ####
    def save_all(self, data):
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def add_restaurants(self, res_dict: dict) -> dict:
        restaurants = self.get_all_restaurants()
        ids = [int(r["id"]) for r in restaurants if str(r.get("id", "")).isdigit()]
        new_res = {"id": max(ids) + 1 if ids else 1, **res_dict}
        restaurants.append(new_res)
        self.save_all(restaurants)
        return new_res

    def update_res(self, res_id: int, update_data: dict):
        restaurants = self.get_all_restaurants()
        for r in restaurants:
            if r.get("id") == res_id:
                r.update(update_data)
                self.save_all(restaurants)
                return r
        return None

    def add_menu_item(self, res_id: int, menu_item_dict: dict):
        restaurants = self.get_all_restaurants()
        for r in restaurants:
            if r.get("id") == res_id:
                if r.get("menu") is None:
                    r["menu"] = []
                r["menu"].append(menu_item_dict)
                self.save_all(restaurants)
                return r
        return None

    def update_menu_item(self, res_id: int, item_name: str, update_data: dict):
        restaurants = self.get_all_restaurants()
        for r in restaurants:
            if r.get("id") == res_id:
                for item in r.get("menu") or []:
                    if str(item.get("Name", "")).strip().lower() == item_name.strip().lower():
                        item.update(update_data)
                        self.save_all(restaurants)
                        return r
        return None