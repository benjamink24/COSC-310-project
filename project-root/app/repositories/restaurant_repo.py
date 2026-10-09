import json
from pathlib import Path


class resRepo:
    def __init__(self, file_path: str = "./data/restaurants.json"):
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

    def save_all(self, data):
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def add_restaurants(self, res_dict: dict) -> dict:
        restaurants = self.get_all_restaurants()
        restaurants.append(res_dict)
        self.save_all(restaurants)
        return res_dict

    def update_res(self, id: int, update_data: dict):
        restaurants = self.get_all_restaurants()
        for r in restaurants:
            # Safely cast both to int so type mismatches don't cause a 404
            if int(r.get("id", -1)) == int(id):
                r.update(update_data)
                self.save_all(restaurants)
                return r
        return None

    def add_menu_item(self, id: int, menu_item_dict: dict):
        restaurants = self.get_all_restaurants()
        for r in restaurants:
            if int(r.get("id", -1)) == int(id):
                if "menu" not in r:
                    r["menu"] = []
                r["menu"].append(menu_item_dict)
                self.save_all(restaurants)
                return r
        return None

    def update_menu_item(self, rest_id: int, item_name: str, update_data: dict):
        restaurants = self.get_all_restaurants()

        print(f"Looking for Restaurant ID: {rest_id}, Menu Item: {item_name}")
        print(f"Loaded restaurants: {restaurants}")

        for r in restaurants:
            raw_id = r.get("id") if r.get("id") is not None else r.get("Id")
            if raw_id is not None:
                try:
                    if int(raw_id) == int(rest_id):
                        menu = r.get("menu") or []
                        for item in menu:
                            current_name = (
                                item.get("name")
                                if item.get("name") is not None
                                else item.get("Name", "")
                            )
                            if (
                                str(current_name).strip().lower()
                                == str(item_name).strip().lower()
                            ):
                                item.update(update_data)
                                self.save_all(restaurants)
                                return r
                except (ValueError, TypeError):
                    continue
        return None
