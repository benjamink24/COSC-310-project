from app.repositories.restaurant_repo import resRepo


class resService:
    def __init__(self, repo: resRepo = resRepo()):
        self.repo = repo

    def get_restaurants(self) -> list:
        return self.repo.get_all_restaurants()


    def create_restaurant(self, restaurant_data: dict) -> dict:
        return self.repo.add_restaurants(restaurant_data)

    def update_restaurant(self, rest_id: int, update_data: dict):
        return self.repo.update_res(rest_id, update_data)

    def add_menu_item(self, id: int, menuItemData: dict) -> dict | None:
        return self.repo.add_menu_item(id, menuItemData)

    def update_menu_item(self, id: int, item_name: str, update_data: dict):
        self.repo.update_menu_item(id, item_name, update_data)

    def get_restaurants_by_name(self, restaurant_name : str ) -> list:
            restaurats_list = self.repo.get_all_restaurants()
            for i in restaurats_list:
                 if i["Name"].lower() == restaurant_name.lower():
                      return i
                 #else:
                    #throw error

    def get_menu_items(self, restaurant_name : str , menu_item: str) -> list:
                restaurats_list = self.repo.get_all_restaurants()
                for i in restaurats_list:
                     if i["Name"].lower() == restaurant_name.lower():
                           for j in i["menu"]:
                                 if j["name"].lower() == menu_item.lower():
                                       return j
                                
                     #else:if
                        #throw error
    
    def get_restaurants_by_cuisine_type(self, cuisine_type : str ) -> list:
            restaurats_list = self.repo.get_all_restaurants()
            filtered_restaurants = []
            for i in restaurats_list:
                if i["Cuisine"].lower() == cuisine_type.lower():
                    filtered_restaurants.append(i)
            return filtered_restaurants
                    
    def get_restaurant_by_id(self, restaurant_id: int) -> dict | None:
        for r in self.repo.get_all_restaurants():
            if int(r.get("id", -1)) == restaurant_id:
                return r
        return None

    def get_menu_by_restaurant_id(self, restaurant_id: int) -> dict | None:
        r = self.get_restaurant_by_id(restaurant_id)
        if r is None:
            return None
        items = [
            {"id": position, **item}
            for position, item in enumerate(r.get("menu", []), start=1)
        ]
        return {
            "restaurant_id": r["id"],
            "restaurant_name": r["Name"],
            "items": items,
        }

    def get_menu_item_by_id(self, restaurant_id: int, item_id: int) -> dict | None:
        menu = self.get_menu_by_restaurant_id(restaurant_id)
        if menu is None:
            return None
        for item in menu["items"]:
            if item["id"] == item_id:
                return item
        return None

