import { apiUrl } from "./api.js";
import { addToCart } from "./cart.js";
import {
    canViewRestaurant,
    currentUser,
    isCustomerUser
} from "./session.js";

let allRestaurants = [];

export function visibleRestaurants(restaurants) {
    if (!currentUser || currentUser.role !== "restaurant") {
        return restaurants;
    }

    return restaurants.filter(
        restaurant => String(restaurant.id) === String(currentUser.restaurantId)
    );
}

function displayRestaurants(restaurants) {
    const restaurantList = document.getElementById("restaurant-list");
    restaurantList.replaceChildren();

    restaurants.forEach(restaurant => {
        const card = document.createElement("div");
        card.className = "restaurant-card";

        const name = document.createElement("h3");
        name.textContent = restaurant.Name;

        const button = document.createElement("button");
        button.type = "button";
        button.textContent = "View Details";
        button.addEventListener("click", () => {
            viewRestaurantDetails(restaurant.id);
        });

        card.append(name, button);
        restaurantList.appendChild(card);
    });
}

function labeledLine(label, value) {
    const paragraph = document.createElement("p");
    const strong = document.createElement("strong");
    strong.textContent = `${label}: `;
    paragraph.append(strong, document.createTextNode(value ?? "N/A"));
    return paragraph;
}

export function searchRestaurants() {
    const searchInput = document
        .getElementById("restaurant-search")
        .value.trim()
        .toLowerCase();

    const selectedCuisine = document
        .getElementById("cuisine-filter")
        .value
        .toLowerCase();

    const status = document.getElementById("status");

    const filteredRestaurants = visibleRestaurants(allRestaurants).filter(restaurant => {
        const name = (restaurant.Name ?? restaurant.name ?? "").toLowerCase();
        const cuisine = (restaurant.Cuisine ?? restaurant.cuisine ?? "").toLowerCase();
        const matchesName = name.includes(searchInput);
        const matchesCuisine =
            selectedCuisine === "" ||
            cuisine === selectedCuisine;
        return matchesName && matchesCuisine;
    });

    displayRestaurants(filteredRestaurants);

    status.textContent = filteredRestaurants.length > 0
        ? `Found ${filteredRestaurants.length} restaurant(s).`
        : "No matching restaurants found.";
}

function populateCuisineFilter(restaurants = visibleRestaurants(allRestaurants)) {
    const cuisineFilter = document.getElementById("cuisine-filter");
    const previousValue = cuisineFilter.value;
    cuisineFilter.replaceChildren();

    const defaultOption = document.createElement("option");
    defaultOption.value = "";
    defaultOption.textContent = "All Cuisines";
    cuisineFilter.appendChild(defaultOption);

    const cuisines = [
        ...new Set(
            restaurants
                .map(restaurant => restaurant.Cuisine ?? restaurant.cuisine)
                .filter(Boolean)
        )
    ].sort();

    cuisines.forEach(cuisine => {
        const option = document.createElement("option");
        option.value = cuisine;
        option.textContent = cuisine;
        cuisineFilter.appendChild(option);
    });

    if ([...cuisineFilter.options].some(option => option.value === previousValue)) {
        cuisineFilter.value = previousValue;
    }
}

async function viewRestaurantDetails(restaurantId) {
    if (!canViewRestaurant(restaurantId)) {
        return;
    }

    const details = document.getElementById("restaurant-details");
    details.textContent = "Loading restaurant details...";

    try {
        const response = await fetch(
            apiUrl(`/restaurants/${encodeURIComponent(restaurantId)}`)
        );

        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        }

        const restaurant = await response.json();
        const heading = document.createElement("h3");
        heading.textContent = restaurant.Name ?? restaurant.name ?? "";

        const menuButton = document.createElement("button");
        menuButton.id = "view-menu-button";
        menuButton.type = "button";
        menuButton.textContent = "View Menu";
        menuButton.addEventListener("click", () => {
            viewRestaurantMenu(restaurantId);
        });

        const menuDisplay = document.createElement("div");
        menuDisplay.id = "menu-display";

        details.replaceChildren(
            heading,
            labeledLine("Cuisine", restaurant.Cuisine ?? restaurant.cuisine ?? "N/A"),
            labeledLine("Address", restaurant.Address ?? restaurant.address ?? "N/A"),
            labeledLine("Hours", restaurant.Hours ?? restaurant.hours ?? "N/A"),
            menuButton,
            menuDisplay
        );
    } catch (error) {
        console.error("Error loading restaurant details:", error);
        details.textContent = "Could not load restaurant details.";
    }
}

async function viewRestaurantMenu(restaurantId) {
    if (!canViewRestaurant(restaurantId)) {
        return;
    }

    const menuDisplay = document.getElementById("menu-display");
    menuDisplay.textContent = "Loading menu...";

    try {
        const response = await fetch(
            apiUrl(`/restaurants/${encodeURIComponent(restaurantId)}/menu`)
        );
        const responseText = await response.text();

        if (!response.ok) {
            throw new Error(
                `Menu request failed: HTTP ${response.status} - ${responseText}`
            );
        }

        const menu = JSON.parse(responseText);
        const items = Array.isArray(menu)
            ? menu
            : menu.menu ?? menu.items ?? menu.menu_items;

        if (!Array.isArray(items) || items.length === 0) {
            menuDisplay.textContent =
                "No menu items found. Check the API response in the console.";
            return;
        }

        const heading = document.createElement("h4");
        heading.textContent = "Restaurant Menu";
        menuDisplay.replaceChildren(heading);

        items.forEach(item => {
            const itemName = typeof item === "string"
                ? item
                : item.name ?? item.Name ?? item.menu_item;

            if (!itemName) {
                console.warn("Menu item has no recognized name:", item);
                return;
            }

            const itemElement = document.createElement("div");
            itemElement.className = "menu-item-row";

            const nameElement = document.createElement("h5");
            nameElement.textContent = itemName;

            const detailsButton = document.createElement("button");
            detailsButton.type = "button";
            detailsButton.textContent = "View Item Details";
            detailsButton.addEventListener("click", () => {
                viewMenuItem(restaurantId, itemName);
            });

            itemElement.append(nameElement, detailsButton);

            if (isCustomerUser()) {
                const addButton = document.createElement("button");
                addButton.type = "button";
                addButton.textContent = "Add to cart";
                if (item && item.Availability === false) {
                    addButton.disabled = true;
                }
                addButton.addEventListener("click", () => {
                    addToCart(restaurantId, itemName);
                });
                itemElement.appendChild(addButton);
            }

            menuDisplay.appendChild(itemElement);
        });
    } catch (error) {
        console.error("Error loading menu:", error);
        menuDisplay.textContent = `Could not load menu: ${error.message}`;
    }
}

async function viewMenuItem(restaurantId, menuItem) {
    if (!canViewRestaurant(restaurantId)) {
        return;
    }

    const menuDisplay = document.getElementById("menu-display");

    try {
        const response = await fetch(
            apiUrl(
                `/restaurants/${encodeURIComponent(restaurantId)}/menu/${encodeURIComponent(menuItem)}`
            )
        );

        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        }

        const item = await response.json();
        const itemDetails = document.createElement("div");
        const heading = document.createElement("h4");
        heading.textContent = "Menu Item Details";

        const name = document.createElement("p");
        name.textContent = `Name: ${item.Name}`;

        const price = document.createElement("p");
        price.textContent = `Price: ${Number(item.Price).toFixed(2)}`;

        const availability = document.createElement("p");
        availability.textContent =
            `Availability: ${item.Availability ? "True" : "False"}`;

        itemDetails.append(heading, name, price, availability);
        menuDisplay.appendChild(itemDetails);
    } catch (error) {
        console.error("Error loading menu item:", error);
        menuDisplay.textContent = "Could not load menu item details.";
    }
}

export async function loadRestaurants() {
    if (!currentUser) {
        return;
    }

    const status = document.getElementById("status");
    status.textContent = "Loading restaurants...";

    try {
        const response = await fetch(apiUrl("/restaurants/"));

        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        }

        allRestaurants = await response.json();
        const availableRestaurants = visibleRestaurants(allRestaurants);
        populateCuisineFilter(availableRestaurants);
        displayRestaurants(availableRestaurants);
        status.textContent = `Found ${availableRestaurants.length} restaurant(s).`;
    } catch (error) {
        console.error("Error loading restaurants:", error);
        status.textContent =
            "Could not load restaurants. Check that FastAPI is running.";
    }
}
