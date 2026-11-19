from app.repositories.customer_repo import customerRepo
from email_validator import EmailNotValidError, validate_email
from app.bloom import UsernameBloomFilter as bloom
from fastapi import HTTPException


class customerService:
    def __init__(self, repo: customerRepo = customerRepo(), bloom_filter: bloom = bloom(1000, 0.01)):
        self.repo = repo
        self.bloom_filter = bloom_filter

    def get_customers(self) -> list:
        return self.repo.get_all_customers()

    def authenticate_customer(self, username: str, password: str) -> bool | None:
        customer = self.repo.get_by_credentials(username, password)
        if customer is False:
            return False
        return True

    def create_customer(self, customer_data: dict) -> dict: # needs to be valid email needs to be accepted payment method, needs to be unqiue username. must be valid names 
        self.check_required_feilds(customer_data)
        self.accepted_payment_method(customer_data.get("paymentMethod"))
        self.validate_email(customer_data.get("email"))
        self.validate_password(customer_data.get("password"))
        self.validate_username(customer_data.get("username"))
        self.bloom_filter.add(customer_data.get("username"))
        return self.repo.add_customer(customer_data)

    def update_customer(self, cId: int, update_data: dict):
        return self.repo.update_customer(cId, update_data)

    def get_customers_by_id(self, cId: int) -> list:
        return self.repo.get_customers_by_id(cId)

    
    def validate_email(email : str):
        try:
            validate_email(email,check_deliverability = False)
        except EmailNotValidError as e:
            raise HTTPException(status_code=422, detail="Unacceptable email")

    def check_required_feilds(customer: dict):
        required_fields = ["Address","emailAddress","paymentMethod","phoneNumber","username", "password"]
        if any(not customer.get(field) for field in required_fields): # 
            raise HTTPException(status_code=422, detail="missing required fields")# unprocessable as the required feilds are needed send back to front end and re promt


    def accepted_payment_method(payment_method:str):
        accepted_payment_methods = ["credit","debit"]
        if any(payment_method.lower()== accepted_payment.lower() for accepted_payment in accepted_payment_methods):
            return
        raise HTTPException(status_code=422, detail="Unacceptable payment method")


    def validate_password(password: str):
            if len(password) <= 5 and password.lower() == password:
                raise HTTPException(status_code=422, detail="Unacceptable password ensure it is longer than 5 charicters and has at least 1 uppercase letter")
    
    def validate_username(self, username: str):
        if self.bloom_filter.might_exist(username):
            raise HTTPException(status_code=422, detail="Username is already taken")
        