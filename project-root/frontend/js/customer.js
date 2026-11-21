import { apiUrl, errorMessageFromResponse } from "./api.js";
import {
    authHeaders,
    canManageRestaurantEndpoints,
    clearSession,
    currentUser,
    isCustomerUser,
    linkedCustomerId
} from "./session.js";

function fillProfile(customer) {
    const profile = document.getElementById("customer-profile");
    profile.replaceChildren();

    const fields = [
        ["Name", `${customer.firstName} ${customer.lastName}`],
        ["Email", customer.emailAddress],
        ["Address", customer.Address],
        ["Phone", customer.phoneNumber],
        ["Payment", customer.paymentMethod]
    ];

    fields.forEach(([label, value]) => {
        const paragraph = document.createElement("p");
        const strong = document.createElement("strong");
        strong.textContent = `${label}: `;
        paragraph.append(strong, document.createTextNode(value ?? "Not provided"));
        profile.appendChild(paragraph);
    });

    const form = document.getElementById("customer-update-form");
    if (!form) {
        return;
    }
    form.elements.firstName.value = customer.firstName ?? "";
    form.elements.lastName.value = customer.lastName ?? "";
    form.elements.Address.value = customer.Address ?? "";
    form.elements.emailAddress.value = customer.emailAddress ?? "";
    form.elements.paymentMethod.value = customer.paymentMethod ?? "credit";
    form.elements.phoneNumber.value = customer.phoneNumber ?? "";
    form.elements.username.value = customer.username ?? currentUser.username ?? "";
}

export async function loadCustomerProfile() {
    if (!isCustomerUser()) {
        return null;
    }

    const status = document.getElementById("customer-status");
    if (linkedCustomerId() === null) {
        status.textContent = "This customer login has no linked customer profile.";
        return null;
    }

    status.textContent = "Loading your customer profile...";

    try {
        const response = await fetch(apiUrl("/customer/me"), {
            headers: authHeaders()
        });

        if (!response.ok) {
            throw new Error(await errorMessageFromResponse(response));
        }

        const customer = await response.json();
        fillProfile(customer);
        status.textContent = "Your customer profile is loaded.";
        return customer;
    } catch (error) {
        console.error("Error loading customer profile:", error);
        status.textContent =
            `Could not load your customer profile: ${error.message}`;
        return null;
    }
}

export async function updateCustomerProfile(event) {
    event.preventDefault();
    const status = document.getElementById("customer-update-status");
    const form = event.currentTarget;
    const submitButton = form.querySelector("button[type='submit']");
    const update = {
        firstName: form.elements.firstName.value.trim(),
        lastName: form.elements.lastName.value.trim(),
        Address: form.elements.Address.value.trim(),
        emailAddress: form.elements.emailAddress.value.trim(),
        paymentMethod: form.elements.paymentMethod.value,
        phoneNumber: form.elements.phoneNumber.value.trim(),
        username: form.elements.username.value.trim(),
        password: form.elements.password.value
    };

    submitButton.disabled = true;
    status.textContent = "Saving profile...";
    try {
        const response = await fetch(apiUrl("/customer/me"), {
            method: "PUT",
            headers: authHeaders({ "Content-Type": "application/json" }),
            body: JSON.stringify(update)
        });
        if (!response.ok) {
            throw new Error(await errorMessageFromResponse(response));
        }
        fillProfile(await response.json());
        form.elements.password.value = "";
        status.textContent = "Profile updated.";
    } catch (error) {
        console.error("Error updating customer profile:", error);
        status.textContent = error.message;
    } finally {
        submitButton.disabled = false;
    }
}

export async function deactivateCustomer() {
    const status = document.getElementById("customer-update-status");
    status.textContent = "Deactivating account...";
    try {
        const response = await fetch(apiUrl("/customer/deactivate"), {
            method: "POST",
            headers: authHeaders()
        });
        if (!response.ok) {
            throw new Error(await errorMessageFromResponse(response));
        }
        clearSession();
        window.location.replace("login.html");
    } catch (error) {
        console.error("Error deactivating customer:", error);
        status.textContent = error.message;
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
    document.getElementById("deactivate-account-button").hidden =
        currentUser.role !== "restaurant";
    document.getElementById("restaurant-app").hidden = false;
    document.getElementById("customer-app").hidden =
        currentUser.role !== "customer";
    document.getElementById("restaurant-management").hidden =
        !canManageRestaurantEndpoints();
    document.getElementById("menu-management").hidden =
        currentUser.role !== "restaurant";
}
