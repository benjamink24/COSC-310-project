from datetime import datetime


from app.repositories.cart_repo import cartRepo
from app.repositories.customer_repo import customerRepo
from app.repositories.history_repo import histRepo
from app.repositories.restaurant_repo import resRepo
from fastapi import HTTPException

class checkoutService:
    def __init__(self, cart_repo=None, history_repo=None, customer_repo=None, res_repo=None):
        self.cart_repo = cart_repo if cart_repo is not None else cartRepo()
        self.history_repo = history_repo if history_repo is not None else histRepo()
        self.customer_repo = customer_repo if customer_repo is not None else customerRepo()
        self.res_repo = res_repo if res_repo is not None else resRepo()

    def _require_customer(self, cId: int) -> None:
        customer = self.customer_repo.get_customers_by_id(cId) 
        if customer is None:
            raise HTTPException(status_code=404, detail="customer not found")
        return customer

    def _required_active_customer(self, cId: int) -> None:
        customer = self._require_customer(cId)
        if customer.get("active") is False:
            raise HTTPException(status_code=403, detail="Account is inactive")
        return customer
        
    def checkout(self, cId: int, paymentMethod: str) -> dict:
        """Turns the customer's cart into a saved order and empties the cart
        The cart only remembers the price from when the item was added every
        line is checked against the menu so a sold out or removed item
        blocks the checkout and price is updated"""

        self._required_active_customer(cId)

        cart = self.cart_repo.get_cart_by_cid(cId)
        if not cart or not cart.get("items"):
            raise HTTPException(status_code=400, detail="cart is empty")

        restaurantId = cart["restaurantId"]
        if self.res_repo.get_restaurants_by_id(restaurantId) is None:
            raise HTTPException(status_code=409, detail="restaurant no longer exists")

        items = []
        for line in cart["items"]:
            menu_item = self.res_repo.get_menu_items(restaurantId, line["Name"])
            if menu_item is None:
                raise HTTPException(status_code=409, detail=f"{line['Name']} is no longer on the menu")
            if not menu_item.get("Availability"):
                raise HTTPException(status_code=409, detail=f"{menu_item['Name']} is no longer available")
            items.append(
                {
                    "Name": menu_item["Name"],
                    "Price": menu_item["Price"],
                    "quantity": line["quantity"],
                }
            )

        order = {
            "cId": cId,
            "restaurantId": restaurantId,
            "items": items,
            "total": round(sum(i["Price"] * i["quantity"] for i in items), 2),
            "paymentMethod": paymentMethod,
            "status": "placed",
            "timestamp": datetime.now().isoformat(),
        }

        # ORDER MATTERS: save the order first, clear the cart second
        saved = self.history_repo.add_order(order)
        if not saved:
            raise HTTPException(status_code=500,detail ="failed to persist order")

        self.cart_repo.clear_cart(cId)
        return saved

    def get_order_history(self, cId: int) -> list:
        self._required_active_customer(cId)
        return self.history_repo.get_orders_by_cid(cId)