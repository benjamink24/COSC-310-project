import { apiUrl } from "./api.js";
import {
    canManageRestaurantEndpoints,
    currentUser,
    isCustomerUser,
    linkedCustomerId
} from "./session.js";

export async function loadCustomerProfile() {
    if (!isCustomerUser()) {
        return null;
    }

    const status = document.getElementById("customer-status");
    const profile = document.getElementById("customer-profile");
    const customerId = linkedCustomerId();

    if (customerId === null) {
        status.textContent = "This customer login has no linked customer profile.";
        return null;
    }

    status.textContent = "Loading your customer profile...";

    try {
        const response = await fetch(apiUrl(`/customer/${customerId}`));

        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        }

        const customer = await response.json();
        profile.replaceChildren();

        const fields = [
            ["Name", `${customer.firstName} ${customer.lastName}`],
            ["Email", customer.emailAddress],
            ["Address", customer.Address]
        ];

        fields.forEach(([label, value]) => {
            const paragraph = document.createElement("p");
            const strong = document.createElement("strong");
            strong.textContent = `${label}: `;
            paragraph.append(strong, document.createTextNode(value ?? "Not provided"));
            profile.appendChild(paragraph);
        });

        status.textContent = "Your customer profile is loaded.";
        return customer;
    } catch (error) {
        console.error("Error loading customer profile:", error);
        status.textContent =
            `Could not load your customer profile: ${error.message}`;
        return null;
    }
}

export function applyAccountChrome() {
    if (!currentUser) {
        window.location.replace("login.html");
        return;
    }

    document.body.dataset.role = currentUser.role;
    document.getElementById("account-name").textContent = currentUser.username;
    const roleLabels = {
        customer: "Customer account",
        restaurant: currentUser.restaurantName || "Restaurant account",
        admin: "Admin account"
    };
    document.getElementById("account-role").textContent = roleLabels[currentUser.role];
    document.getElementById("restaurant-app").hidden = false;
    document.getElementById("customer-app").hidden =
        currentUser.role !== "customer";
    document.getElementById("restaurant-management").hidden =
        !canManageRestaurantEndpoints();
    document.getElementById("menu-management").hidden =
        currentUser.role !== "restaurant";
}
