import { apiUrl } from "./api.js";
import { loadMenuRestaurants } from "./menu-management.js";
import { loadRestaurants } from "./restaurants.js";
import {
    canManageRestaurant,
    currentUser,
    isRestaurantUser,
    ownerAuthHeaders
} from "./session.js";

const operationSelect = document.getElementById("operation");
const manageIdSelect = document.getElementById("manage-id");
const restaurantForm = document.getElementById("restaurant-form");
const saveButton = document.getElementById("save-button");
const formStatus = document.getElementById("form-status");
const createRestaurantOption = operationSelect.querySelector(
    'option[value="create"]'
);
const updateRestaurantOption = operationSelect.querySelector(
    'option[value="update"]'
);
const manageIdLabel = document.getElementById("manage-id-label");

let selectedRestaurant = null;

function clearRestaurantForm() {
    restaurantForm.reset();
    selectedRestaurant = null;
}

async function loadSelectedRestaurant() {
    const restaurantId = manageIdSelect.value;

    clearRestaurantForm();
    formStatus.textContent = "";

    if (!restaurantId) {
        return;
    }
    if (!canManageRestaurant(restaurantId)) {
        formStatus.textContent =
            "This login can only manage its assigned restaurant.";
        return;
    }

    try {
        const [detailsResponse, menuResponse] = await Promise.all([
            fetch(apiUrl(`/restaurants/${encodeURIComponent(restaurantId)}`)),
            fetch(apiUrl(`/restaurants/${encodeURIComponent(restaurantId)}/menu`))
        ]);

        if (!detailsResponse.ok) {
            throw new Error(`Restaurant request failed: HTTP ${detailsResponse.status}`);
        }

        if (!menuResponse.ok) {
            throw new Error(`Menu request failed: HTTP ${menuResponse.status}`);
        }

        const restaurant = await detailsResponse.json();
        const menu = await menuResponse.json();
        if (!Array.isArray(menu)) {
            throw new Error("The menu API did not return a list.");
        }

        selectedRestaurant = {
            ...restaurant,
            id: Number(restaurantId),
            Photos: [],
            menu
        };

        document.getElementById("name").value = restaurant.Name ?? "";
        document.getElementById("cuisine").value = restaurant.Cuisine ?? "";
        document.getElementById("address").value = restaurant.Address ?? "";
        document.getElementById("hours").value = restaurant.Hours ?? "";
        document.getElementById("photos").value =
            (restaurant.Photos ?? []).join("\n");
    } catch (error) {
        console.error("Error loading restaurant:", error);
        formStatus.textContent = "Could not load restaurant details.";
    }
}

export async function loadManageRestaurants() {
    if (!isRestaurantUser()) {
        return;
    }

    try {
        const response = await fetch(apiUrl("/restaurants/"));

        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        }

        const restaurants = await response.json();
        manageIdSelect.replaceChildren();

        const placeholder = document.createElement("option");
        placeholder.value = "";
        placeholder.textContent = "Select a restaurant";
        manageIdSelect.appendChild(placeholder);

        const manageableRestaurants = restaurants.filter(
            restaurant => canManageRestaurant(restaurant.id)
        );

        manageableRestaurants.forEach(restaurant => {
            const option = document.createElement("option");
            option.value = String(restaurant.id);
            option.textContent = restaurant.Name;
            manageIdSelect.appendChild(option);
        });

        if (manageableRestaurants.length === 0) {
            formStatus.textContent = "No restaurant is assigned to this login.";
            return;
        }

        manageIdSelect.value = String(currentUser.restaurantId);
        await loadSelectedRestaurant();
    } catch (error) {
        console.error("Error loading restaurants:", error);
        formStatus.textContent = "Could not load restaurants. Please try again.";
    }
}

async function saveRestaurant(event) {
    event.preventDefault();

    if (!currentUser || !["restaurant", "admin"].includes(currentUser.role)) {
        return;
    }

    const operation = operationSelect.value;
    const restaurantId = manageIdSelect.value;

    if (
        (currentUser.role === "restaurant" &&
            (operation !== "update" || !canManageRestaurant(restaurantId))) ||
        (currentUser.role === "admin" && operation !== "create")
    ) {
        formStatus.textContent = "This account cannot perform that action.";
        return;
    }

    if (operation === "update" && !selectedRestaurant) {
        formStatus.textContent =
            "Please select a restaurant and wait for its details to load.";
        return;
    }

    const restaurantData = {
        Name: document.getElementById("name").value.trim(),
        Cuisine: document.getElementById("cuisine").value.trim(),
        Address: document.getElementById("address").value.trim(),
        Hours: document.getElementById("hours").value.trim(),
        Photos: document.getElementById("photos").value
            .split("\n")
            .map(url => url.trim())
            .filter(url => url !== ""),
        menu: operation === "update" ? selectedRestaurant.menu ?? [] : []
    };

    const url = operation === "create"
        ? apiUrl("/restaurants/")
        : apiUrl(`/restaurants/${encodeURIComponent(restaurantId)}`);
    const method = operation === "create" ? "POST" : "PUT";

    try {
        saveButton.disabled = true;
        saveButton.textContent = operation === "create"
            ? "Creating..."
            : "Updating...";

        const response = await fetch(url, {
            method,
            headers: ownerAuthHeaders({
                "Content-Type": "application/json"
            }),
            body: JSON.stringify(restaurantData)
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP ${response.status}: ${errorText}`);
        }

        formStatus.textContent = operation === "create"
            ? "Restaurant created successfully!"
            : "Restaurant updated successfully!";

        await loadManageRestaurants();
        await loadMenuRestaurants();
        await loadRestaurants();

        if (operation === "create") {
            clearRestaurantForm();
        }
    } catch (error) {
        console.error("Error saving restaurant:", error);
        formStatus.textContent = `Failed to save restaurant: ${error.message}`;
    } finally {
        saveButton.disabled = false;
        saveButton.textContent = operationSelect.value === "create"
            ? "Create Restaurant"
            : "Update Restaurant";
    }
}

export function initRestaurantManagement() {
    if (currentUser && currentUser.role === "restaurant") {
        createRestaurantOption.hidden = true;
        createRestaurantOption.disabled = true;
        operationSelect.value = "update";
        operationSelect.disabled = true;
        manageIdSelect.disabled = false;
        manageIdSelect.required = true;
        saveButton.textContent = "Update Restaurant";
    } else if (currentUser && currentUser.role === "admin") {
        updateRestaurantOption.hidden = true;
        updateRestaurantOption.disabled = true;
        operationSelect.value = "create";
        operationSelect.disabled = true;
        manageIdLabel.hidden = true;
        manageIdSelect.hidden = true;
    }

    operationSelect.addEventListener("change", () => {
        const isUpdate = operationSelect.value === "update";
        manageIdSelect.disabled = !isUpdate;
        manageIdSelect.required = isUpdate;
        saveButton.textContent = isUpdate
            ? "Update Restaurant"
            : "Create Restaurant";
        formStatus.textContent = "";
        clearRestaurantForm();
    });

    manageIdSelect.disabled = true;
    manageIdSelect.required = false;
    manageIdSelect.addEventListener("change", loadSelectedRestaurant);
    restaurantForm.addEventListener("submit", saveRestaurant);
}
