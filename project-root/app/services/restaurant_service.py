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
                    
    

