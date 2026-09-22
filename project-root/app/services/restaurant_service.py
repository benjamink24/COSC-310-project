from app.repositories.restaurant_repo import resRepo
class resService:
    def __init__(self, repo: resRepo = resRepo()):
        self.repo = repo
        
    def get_restaurants(self) -> list:
        return self.repo.get_all_restaurants
    