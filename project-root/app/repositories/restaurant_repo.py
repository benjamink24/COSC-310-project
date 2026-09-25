import json
from pathlib import Path

class resRepo:
    def __init__(self, file_path: str="../data/restaurants.json"):
        self.file_path: Path = Path(file_path)
        
        
    def get_all_restaurants(self) -> list:
        if not self.file_path.exists(): 
            return []
        with open(self.file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("restaurants", [])
        