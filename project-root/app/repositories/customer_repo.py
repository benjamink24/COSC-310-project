import json
from pathlib import Path
import os
from .repository import AbstractRepository

class customerRepo(AbstractRepository):
    def __init__(self, file_path: str | None = None):
        if file_path is None:
            file_path =  "./data/customers.json" #causes error as the file switches "./data/test.json" if running_tests() else
        self.file_path: Path = Path(file_path)

    def get_all(self) -> list:
        if not self.file_path.exists():
                    return []
        with open(self.file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return data.get("customers", [])
    
    def get_by_field(self, field: str, value: str) -> list:
            customers = self.get_all()
            filtered = []
            for c in customers:
                if str(field).strip().lower() == "cId":
                    if "cId" in c and str(c.get("cId")) == str(value):
                        filtered.append(c)
                else:
                    if str(c.get(field, "")).strip().lower() == str(value).strip().lower():
                        filtered.append(c)
            return filtered
    def get_all_customers(self) -> list:
                return self.get_all()


    def add_customer(self, customer_dict: dict) -> dict:
                customers = self.get_all_customers()
                if customers and "cId" in customers[-1]:
                    new_id = int(customers[-1]["cId"]) + 1
                else:
                    new_id = 1
                customer_dict["orderHistory"] = []
                customer_dict["active"] = True
                customer_dict["cId"] = new_id
                customers.append(customer_dict)
                self.save_all(customers)
                return customer_dict
   
    
    def update_customer(self, cId, update_data: dict) -> dict:
                customers = self.get_all_customers()
                for c in customers:
                    if "cId" in c and str(c.get("cId")) == str(cId): #why cast as string if both are ints?
                        c.update(update_data)
                        self.save_all(customers)
                        return c
                return None
     
    def add(self, item_dict: dict) -> dict:
        return self.add_customer(item_dict)
        
    def get_customers_by_id(self, cId) -> dict:
        results = self.get_by_field("cId", cId)
        return results[0] if results else None
    
    def update(self, identifier, update_data: dict) -> dict:
        return self.update_customer(identifier, update_data)
    
    def save_all(self, data):
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    
        
    
    
        
    
        
    