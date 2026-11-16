from app.repositories.cart_repo import cartRepo
from app.repositories.customer_repo import customerRepo
from app.repositories.restaurant_repo import resRepo
from fastapi import HTTPException

def _same(a, b) -> bool:
    """Case-insensitive name comparison, same rule resRepo.get_menu_items uses."""
    return str(a).strip().lower() == str(b).strip().lower()

def _with_total(cart: dict) -> dict:
    """What the API returns: the stored cart plus a computed total.
    The total is never stored in cart.json, so it can't go stale."""
    total = round(sum(i["Price"] * i["quantity"] for i in cart["items"]), 2)
    return {
        "cId": cart["cId"],
        "restaurantId": cart["restaurantId"],
        "items": cart["items"],
        "total": total,
    }

class cartService:
    def __init__(self, cart_repo=None, res_repo=None, customer_repo=None):
        self.cart_repo = cart_repo if cart_repo is not None else cartRepo()
        self.res_repo = res_repo if res_repo is not None else resRepo()
        self.customer_repo = customer_repo if customer_repo is not None else customerRepo()

    def _require_customer(self, cId: int) -> None:
        if self.customer_repo.get_customers_by_id(cId) is None:
            raise HTTPException(status_code=404, detail="customer not found")

    def get_cart(self, cId: int) -> dict | None:
        """The customer cart with its total or None if they have no cart"""
        self._require_customer(cId)
        cart = self.cart_repo.get_cart_by_cid(cId)
        if cart is None:
            return None
        return _with_total(cart)

    def add_item(self, cId: int, restaurantId: int, Name: str, quantity: int) -> dict:
        self._require_customer(cId)
        if self.res_repo.get_restaurants_by_id(restaurantId) is None:
            raise HTTPException(status_code=404, detail="restaurant not found")
        menu_item = self.res_repo.get_menu_items(restaurantId, Name)
        if menu_item is None:
            raise HTTPException(status_code=404, detail="menu item not found")
        if not menu_item.get("Availability"):
            raise HTTPException(status_code=409, detail=f"{menu_item['Name']} is currently unavailable")

        cart = self.cart_repo.get_cart_by_cid(cId)
        if cart is None:
            cart = {"cId": cId, "restaurantId": restaurantId, "items": []}
        elif cart["items"] and str(cart["restaurantId"]) != str(restaurantId):
            raise HTTPException(status_code=409, detail="cart already has items from another restaurant")
        else:
            cart["restaurantId"] = restaurantId

        for line in cart["items"]:
            if _same(line["Name"], menu_item["Name"]):
                line["quantity"] += quantity
                break
        else:
            cart["items"].append(
                {"Name": menu_item["Name"], "Price": menu_item["Price"], "quantity": quantity}
            )

        self.cart_repo.save_cart(cart)
        return _with_total(cart)

    def update_item(self, cId: int, Name: str, quantity: int) -> dict:
        """SETS a line's quantity (add_item, by contrast, adds to it)."""
        cart = self.cart_repo.get_cart_by_cid(cId)
        if cart is None:
            raise HTTPException(status_code=404, detail="cart not found")
        for line in cart["items"]:
            if _same(line["Name"], Name):
                line["quantity"] = quantity
                self.cart_repo.save_cart(cart)
                return _with_total(cart)
        raise HTTPException(status_code=404, detail="item not in cart")

    def remove_item(self, cId: int, Name: str) -> dict:
        """ Removes a line leaves an empty cart behind (clear_cart to delete cart)."""
        cart = self.cart_repo.get_cart_by_cid(cId)
        if cart is None:
            raise HTTPException(status_code=404, detail="cart not found")
        remaining = [line for line in cart["items"] if not _same(line["Name"], Name)]
        if len(remaining) == len(cart["items"]):
            raise HTTPException(status_code=404, detail="item not in cart")
        cart["items"] = remaining
        self.cart_repo.save_cart(cart)
        return _with_total(cart)

    def clear_cart(self, cId: int) -> bool:
        """Deletes the whole cart goes False if there was nothing to delete"""
        return self.cart_repo.clear_cart(cId)