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

    ####
    def get_restaurants_by_name(self, restaurant_name: str) -> list:
        restaurats_list = self.get_all_restaurants()
        for i in restaurats_list:
            if i["Name"].lower() == restaurant_name.strip().lower():
                return i

        return None

    def get_menu_items(self, restaurant_name: str, menu_item: str) -> list:
        restaurats_list = self.get_all_restaurants()
        for i in restaurats_list:
            if i["Name"].lower() == restaurant_name.lower():
                for j in i["menu"]:
                    if j["Name"].lower() == menu_item.lower():
                        return j
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
        id=restaurants[-1]["id"]+1
        id_dict={"id":id}
        id_res_dict= id_dict | res_dict
        restaurants.append(id_res_dict)
        ids = []
        for r in restaurants:
            if str(r.get("id", "")).isdigit():
                ids.append(int(r["id"]))
        next_id = max(ids) + 1 if ids else 1
        res_dict["id"] = next_id
        restaurants.append(res_dict)
        self.save_all(restaurants)
        
        return res_dict

    def update_res(self, res_name: str, update_data: dict):
        restaurants = self.get_all_restaurants()
        for r in restaurants:
            current_name = r.get("Name")
            if str(current_name).strip().lower() == str(res_name).strip().lower():
                r.update(update_data)
                self.save_all(restaurants)
                return r
        return None

    def add_menu_item(self, res_name: str, menu_item_dict: dict):
        restaurants = self.get_all_restaurants()
        for r in restaurants:
            current_res_name = r.get("Name") or r.get("name", "")
            if str(current_res_name).strip().lower() == str(res_name).strip().lower():
                if "menu" not in r or r["menu"] is None:
                    r["menu"] = []
                r["menu"].append(menu_item_dict)
                self.save_all(restaurants)
                return r
        return None

    def update_menu_item(self, res_name: str, item_name: str, update_data: dict):
        restaurants = self.get_all_restaurants()

        for r in restaurants:
            current_res_name = r.get("Name") or r.get("Name", "")
            if str(current_res_name).strip().lower() == str(res_name).strip().lower():
                menu = r.get("menu") or []
                for item in menu:
                    current_item_name = item.get("Name") or item.get("Name", "")
                    if (
                        str(current_item_name).strip().lower()
                        == str(item_name).strip().lower()
                    ):
                        item.update(update_data)
                        self.save_all(restaurants)
                        return r
        return None
