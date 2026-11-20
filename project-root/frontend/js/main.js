import { apiUrl } from "./api.js";
import { showCartUnavailable, startCart } from "./cart.js";
import { applyAccountChrome, loadCustomerProfile } from "./customer.js";
import { initMenuManagement, loadMenuRestaurants, updateMenuForm } from "./menu-management.js";
import { initRestaurantManagement, loadManageRestaurants } from "./restaurant-management.js";
import { loadRestaurants, searchRestaurants } from "./restaurants.js";
import {
    clearSession,
    currentUser,
    isCustomerUser,
    isRestaurantUser,
    linkedCustomerId
} from "./session.js";

applyAccountChrome();

document.getElementById("logout-button").addEventListener("click", () => {
    const finishLogout = () => {
        clearSession();
        window.location.replace("login.html");
    };
    const accessToken = currentUser && currentUser.accessToken;
    if (!accessToken) {
        finishLogout();
        return;
    }

    fetch(apiUrl("/restaurant-owners/logout"), {
        method: "POST",
        headers: { Authorization: `Bearer ${accessToken}` }
    })
        .catch(error => console.error("Could not end server session:", error))
        .finally(finishLogout);
});

initRestaurantManagement();
initMenuManagement();

if (currentUser) {
    const boot = async () => {
        if (isCustomerUser()) {
            const customer = await loadCustomerProfile();
            const customerId = linkedCustomerId();
            if (customerId === null) {
                showCartUnavailable();
            } else {
                const payment = document.getElementById("payment-method");
                if (payment && customer && customer.paymentMethod) {
                    payment.value = customer.paymentMethod;
                }
                await startCart(customerId);
            }
        }

        await loadRestaurants();

        document
            .getElementById("restaurant-search")
            .addEventListener("input", searchRestaurants);
        document
            .getElementById("cuisine-filter")
            .addEventListener("change", searchRestaurants);

        if (isRestaurantUser()) {
            await loadManageRestaurants();
            await loadMenuRestaurants();
            updateMenuForm();
        }
    };

    boot();
}
