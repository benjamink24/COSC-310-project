import { apiUrl, errorMessageFromResponse } from "./api.js";
import {
    canManageRestaurant,
    currentUser,
    isRestaurantUser,
    ownerAuthHeaders
} from "./session.js";

const menuOperationSelect = document.getElementById("menu-operation");
const menuSaveButton = document.getElementById("menu-save-button");
const restaurantSelect = document.getElementById("menu-restaurant-id");
const itemSelect = document.getElementById("menu-item-id");
const menuForm = document.getElementById("menu-form");
const nameInput = document.getElementById("menu-name");
const priceInput = document.getElementById("menu-price");
const availabilitySelect = document.getElementById("menu-availability");
const statusMessage = document.getElementById("menu-status");

let currentMenuItems = [];

export function updateMenuForm() {
    const operation = menuOperationSelect ? menuOperationSelect.value : "create";
    const isUpdate = operation === "update";

    itemSelect.style.display = isUpdate ? "block" : "none";
    itemSelect.required = isUpdate;

    if (menuSaveButton) {
        menuSaveButton.textContent = isUpdate
            ? "Update Menu Item"
            : "Add Menu Item";
    }

    nameInput.value = "";
    priceInput.value = "";
    availabilitySelect.value = "true";
    statusMessage.textContent = "";

    loadMenuItems();
}

export async function loadMenuRestaurants() {
    if (!isRestaurantUser()) {
        return;
    }

    try {
        const response = await fetch(apiUrl("/restaurants"));

        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        }

        const restaurants = await response.json();
        restaurantSelect.replaceChildren();

        const placeholder = document.createElement("option");
        placeholder.value = "";
        placeholder.textContent = "Select a restaurant";
        restaurantSelect.appendChild(placeholder);

        const manageableRestaurants = restaurants.filter(
            restaurant => canManageRestaurant(restaurant.id)
        );

        manageableRestaurants.forEach(restaurant => {
            const option = document.createElement("option");
            option.value = String(restaurant.id);
            option.textContent = restaurant.Name;
            restaurantSelect.appendChild(option);
        });

        if (manageableRestaurants.length > 0) {
            restaurantSelect.value = String(currentUser.restaurantId);
            await loadMenuItems();
        }
    } catch (error) {
        console.error("Error loading restaurants:", error);
        statusMessage.textContent = "Could not load restaurants.";
    }
}

export async function loadMenuItems() {
    if (!isRestaurantUser()) {
        return;
    }

    const restaurantId = restaurantSelect.value;
    itemSelect.replaceChildren();

    const placeholder = document.createElement("option");
    placeholder.value = "";
    placeholder.textContent = "Select a menu item";
    itemSelect.appendChild(placeholder);

    if (!restaurantId) {
        return;
    }
    if (!canManageRestaurant(restaurantId)) {
        statusMessage.textContent =
            "This login can only manage its assigned restaurant.";
        return;
    }

    try {
        const response = await fetch(
            apiUrl(`/restaurants/${encodeURIComponent(restaurantId)}/menu`)
        );

        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        }

        const menuItems = await response.json();
        currentMenuItems = menuItems;

        if (!Array.isArray(menuItems)) {
            throw new Error("The menu API did not return a list.");
        }

        menuItems.forEach((item, index) => {
            const option = document.createElement("option");
            option.value = String(index);
            option.textContent =
                `${item.Name} - $${Number(item.Price).toFixed(2)} ` +
                `(${item.Availability ? "Available" : "Unavailable"})`;
            itemSelect.appendChild(option);
        });

        if (menuItems.length === 0) {
            statusMessage.textContent =
                "No menu items found for this restaurant.";
        } else {
            statusMessage.textContent =
                `Loaded ${menuItems.length} menu item(s).`;
        }
    } catch (error) {
        console.error("Error loading menu items:", error);
        statusMessage.textContent =
            `Could not load menu items: ${error.message}`;
    }
}

function selectMenuItem() {
    const index = itemSelect.value;

    if (index === "") {
        nameInput.value = "";
        priceInput.value = "";
        availabilitySelect.value = "true";
        return;
    }

    const item = currentMenuItems[Number(index)];
    if (!item) {
        return;
    }

    nameInput.value = item.Name;
    priceInput.value = item.Price;
    availabilitySelect.value = String(item.Availability);
}

async function saveMenuItem(event) {
    event.preventDefault();

    if (!isRestaurantUser()) {
        return;
    }

    const restaurantId = restaurantSelect.value;
    const operation = menuOperationSelect ? menuOperationSelect.value : "create";
    const selectedIndex = itemSelect.value;
    const itemName =
        selectedIndex !== "" &&
        currentMenuItems &&
        currentMenuItems[Number(selectedIndex)]
            ? currentMenuItems[Number(selectedIndex)].Name
            : "";
    const submitButton = document.querySelector("#menu-form button[type='submit']")
        || menuSaveButton;

    if (!restaurantId) {
        statusMessage.textContent = "Please select a restaurant.";
        return;
    }
    if (!canManageRestaurant(restaurantId)) {
        statusMessage.textContent =
            "This login can only manage its assigned restaurant.";
        return;
    }

    if (operation === "update" && !itemName) {
        statusMessage.textContent = "Please select a menu item to update.";
        return;
    }

    const menuData = {
        Name: nameInput.value.trim(),
        Price: Number(priceInput.value),
        Availability: availabilitySelect.value === "true"
    };

    if (!menuData.Name) {
        statusMessage.textContent = "Menu item name is required.";
        return;
    }

    let url = apiUrl(`/restaurants/${encodeURIComponent(restaurantId)}/menu`);
    let method = "POST";

    if (operation === "update") {
        url += `/${encodeURIComponent(itemName)}`;
        method = "PUT";
    }

    try {
        submitButton.disabled = true;
        statusMessage.textContent = "Saving menu item...";

        const response = await fetch(url, {
            method,
            headers: ownerAuthHeaders({
                "Content-Type": "application/json"
            }),
            body: JSON.stringify(menuData)
        });

        if (!response.ok) {
            throw new Error(
                await errorMessageFromResponse(response) ||
                `HTTP error: ${response.status}`
            );
        }

        statusMessage.textContent = operation === "create"
            ? "Menu item added successfully!"
            : "Menu item updated successfully!";

        await loadMenuItems();

        if (operation === "create") {
            menuForm.reset();
            availabilitySelect.value = "true";
        }
    } catch (error) {
        console.error("Error saving menu item:", error);
        statusMessage.textContent = `Failed to save menu item: ${error.message}`;
    } finally {
        submitButton.disabled = false;
    }
}

export function initMenuManagement() {
    restaurantSelect.addEventListener("change", loadMenuItems);
    if (menuOperationSelect) {
        menuOperationSelect.addEventListener("change", updateMenuForm);
    }
    itemSelect.addEventListener("change", selectMenuItem);
    menuForm.addEventListener("submit", saveMenuItem);
}
