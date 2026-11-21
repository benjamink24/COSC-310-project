import { apiUrl } from "./api.js";
import { showCartUnavailable, startCart } from "./cart.js";
import {
    applyAccountChrome,
    deactivateCustomer,
    loadCustomerProfile,
    updateCustomerProfile
} from "./customer.js";
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

    const logoutPath = currentUser.role === "customer"
        ? "/customer/logout"
        : "/restaurant-owners/logout";
    fetch(apiUrl(logoutPath), {
        method: "POST",
        headers: { Authorization: `Bearer ${accessToken}` }
    })
        .catch(error => console.error("Could not end server session:", error))
        .finally(finishLogout);
});

document.getElementById("deactivate-account-button").addEventListener("click", async () => {
    if (!isRestaurantUser() || !currentUser.accessToken) {
        return;
    }
    try {
        const response = await fetch(apiUrl("/restaurant-owners/deactivate"), {
            method: "POST",
            headers: { Authorization: `Bearer ${currentUser.accessToken}` }
        });
        if (!response.ok) {
            const message = await response.text();
            throw new Error(message || `HTTP error: ${response.status}`);
        }
        clearSession();
        window.location.replace("login.html");
    } catch (error) {
        console.error("Could not deactivate account:", error);
        window.alert(`Could not deactivate account: ${error.message}`);
    }
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
                document
                    .getElementById("customer-update-form")
                    .addEventListener("submit", updateCustomerProfile);
                document
                    .getElementById("deactivate-customer-button")
                    .addEventListener("click", deactivateCustomer);
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
