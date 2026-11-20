from app.repositories.restaurant_repo import resRepo
from fastapi import HTTPException

class resService:
    def __init__(self, repo: resRepo = resRepo()):
        self.repo = repo

    def get_restaurants(self) -> list:
        return self.repo.get_all_restaurants()

    def get_restaurants_by_name(self, restaurant_name: str) -> list:
        return self.repo.get_restaurants_by_name(restaurant_name)
                
    
    def get_restaurants_by_id(self, restaurant_id: int) -> list:
        return self.repo.get_restaurants_by_id(restaurant_id)
    
    def get_menu_items(self, restaurant_id: int, menu_item: str) -> list:
        return self.repo.get_menu_items(restaurant_id,menu_item)

    def get_restaurants_by_cuisine_type(self, cuisine_type: str) -> list:
        return self.repo.get_restaurants_by_cuisine_type(cuisine_type)

   
   
    def create_restaurant(self, restaurant_data: dict) -> dict:
        resService.validate_missing_res_feilds(restaurant_data)
        return self.repo.add_restaurants(restaurant_data)

    def update_restaurant(self, res_id: int, update_data: dict):
        resService.validate_missing_res_feilds(update_data)
        return self.repo.update_res(res_id, update_data)

   
   
    def add_menu_item(self, res_id: int, menuItemData: dict) -> dict | None:
        resService.validate_missing_menu_feilds(menuItemData)
        resService.validate_non_negative(menuItemData)
        return self.repo.add_menu_item(res_id, menuItemData)

    def update_menu_item(self, res_id: int, item_name: str, update_data: dict):
        resService.validate_missing_menu_feilds(update_data)
        resService.validate_non_negative(update_data)
        return self.repo.update_menu_item(res_id, item_name, update_data)

    @staticmethod
    def validate_missing_menu_feilds(menu_item_data: dict):
        required_fields = ["Name","Price","Availability"]
        for field in required_fields: 
            if menu_item_data.get(field) is None:
                raise HTTPException(status_code=422, detail="missing required feild") 

    @staticmethod
    def validate_non_negative(menu_item_data: dict):
        if menu_item_data.get("Price") <0:
            raise  HTTPException(status_code=422, detail="price cannot be negative") 


    @staticmethod
    def validate_missing_res_feilds(res_item_data: dict):
            required_fields = ["Name","Cuisine","Address","Hours"]
            for field in required_fields: 
                if res_item_data.get(field) is None:
                    raise HTTPException(status_code=422, detail="missing required feild") 
        

    
