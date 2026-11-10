from app.repositories.customer_repo import customerRepo


class customerService:
    def __init__(self, repo: customerRepo = customerRepo()):
        self.repo = repo

    def get_customers(self) -> list:
        return self.repo.get_all_customers()

    def create_customer(self, customer_data: dict) -> dict:
        return self.repo.add_customer(customer_data)

    def update_customer(self, res_id: int, update_data: dict):
        return self.repo.update_customer(res_id, update_data)     

    def get_customers_by_id(self, cId: int) -> list:
        return self.repo.get_customers_by_id(cId)

    
