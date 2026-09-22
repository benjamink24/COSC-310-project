import json
from pathLib import path

class resRepo:
    def __init__(self, file_path: str="data/restaurant.json"):
        self.file_path = Path(file_path)
        
        
    def get_all_restaurants(self) -> list:
        if not self.file_path.exists(): return []
        with open(self.file_path, "r") as f:
            data = json.load(f)
            return data.get(restaurants, [])
        