
const API_URL = "http://127.0.0.1:8000";

const operationSelect = document.getElementById("operation");
const menuOperationSelect = document.getElementById("menu-operation");
const menuSaveButton = document.getElementById("menu-save-button");
const manageIdSelect = document.getElementById("manage-id");
const restaurantForm = document.getElementById("restaurant-form");
const saveButton = document.getElementById("save-button");
const formStatus = document.getElementById("form-status");
const restaurantSelect = document.getElementById("menu-restaurant-id");
const itemSelect = document.getElementById("menu-item-id");
const menuForm = document.getElementById("menu-form");
const nameInput = document.getElementById("menu-name");
const priceInput = document.getElementById("menu-price");
const availabilitySelect = document.getElementById("menu-availability");
const statusMessage = document.getElementById("menu-status");

let allRestaurants = [];

// GET /restaurants/ - List Restaurants
async function loadRestaurants() {
    const status = document.getElementById("status");

    status.textContent = "Loading restaurants...";

    try {
        const response = await fetch(`${API_URL}/restaurants/`);

        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        }

        allRestaurants = await response.json();

        populateCuisineFilter();
        displayRestaurants(allRestaurants);
        
        status.textContent = `Found ${allRestaurants.length} restaurant(s).`;

    } catch (error) {
        console.error("Error loading restaurants:", error);
        status.textContent =
            "Could not load restaurants. Check that FastAPI is running.";
    }
}

// Display restaurant cards
function displayRestaurants(restaurants) {
    const restaurantList = document.getElementById("restaurant-list");

    restaurantList.innerHTML = "";

    restaurants.forEach(restaurant => {
        const card = document.createElement("div");
        card.className = "restaurant-card";

        const name = document.createElement("h3");
        name.textContent = restaurant.Name;

        const button = document.createElement("button");
        button.textContent = "View Details";

        button.addEventListener("click", () => {
            viewRestaurantDetails(restaurant.Name);
        });

        card.appendChild(name);
        card.appendChild(button);

        restaurantList.appendChild(card);
    });
}

// Search by restaurant name
function searchRestaurants() {
    const searchInput = document
        .getElementById("restaurant-search")
        .value.trim()
        .toLowerCase();

    const selectedCuisine = document
        .getElementById("cuisine-filter")
        .value
        .toLowerCase();

    const status = document.getElementById("status");

    // Filter the restaurants already loaded from the API
    const filteredRestaurants = allRestaurants.filter(restaurant => {
        const name = (restaurant.Name ?? restaurant.name ?? "")
            .toLowerCase();

        const cuisine = (restaurant.Cuisine ?? restaurant.cuisine ?? "")
            .toLowerCase();

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

// Populate the cuisine filter
function populateCuisineFilter() {
    const cuisineFilter = document.getElementById("cuisine-filter");

    cuisineFilter.innerHTML = "";

    const defaultOption = document.createElement("option");
    defaultOption.value = "";
    defaultOption.textContent = "All Cuisines";
    cuisineFilter.appendChild(defaultOption);

    const cuisines = [
        ...new Set(
            allRestaurants
                .map(restaurant =>
                    restaurant.Cuisine ?? restaurant.cuisine
                )
                .filter(Boolean)
        )
    ].sort();

    cuisines.forEach(cuisine => {
        const option = document.createElement("option");
        option.value = cuisine;
        option.textContent = cuisine;
        cuisineFilter.appendChild(option);
    });
}

// Display the selected restaurant's details
async function viewRestaurantDetails(restaurantName) {
    const details = document.getElementById("restaurant-details");

    details.textContent = "Loading restaurant details...";

    try {
        const response = await fetch(
            `${API_URL}/restaurants/${encodeURIComponent(restaurantName)}`
        );

        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        }

        const restaurant = await response.json();
        selectedRestaurant = restaurant;

        details.innerHTML = `
            <h3>${restaurant.Name ?? restaurant.name}</h3>
            <p><strong>Cuisine:</strong> ${restaurant.Cuisine ?? restaurant.cuisine ?? "N/A"}</p>
            <p><strong>Address:</strong> ${restaurant.Address ?? restaurant.address ?? "N/A"}</p>
            <p><strong>Hours:</strong> ${restaurant.Hours ?? restaurant.hours ?? "N/A"}</p>

            <button id="view-menu-button">View Menu</button>

            <div id="menu-display"></div>
        `;

        document.getElementById("view-menu-button")
            .addEventListener("click", () => {
                viewRestaurantMenu(restaurantName);
            });

    } catch (error) {
        console.error("Error loading restaurant details:", error);
        details.textContent = "Could not load restaurant details.";
    }
}

// Display all menu items for the selected restaurant
async function viewRestaurantMenu(restaurantName) {
    const menuDisplay = document.getElementById("menu-display");

    menuDisplay.textContent = "Loading menu...";

    try {
        const url =
            `${API_URL}/restaurants/${encodeURIComponent(restaurantName)}/menu`;


        const response = await fetch(url);
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

        menuDisplay.innerHTML = "<h4>Restaurant Menu</h4>";

        items.forEach(item => {
            const itemName = typeof item === "string"
                ? item
                : item.name ?? item.Name ?? item.menu_item;

            if (!itemName) {
                console.warn("Menu item has no recognized name:", item);
                return;
            }

            const itemElement = document.createElement("div");
            const nameElement = document.createElement("h5");
            const button = document.createElement("button");

            nameElement.textContent = itemName;
            button.textContent = "View Item Details";

            button.addEventListener("click", () => {
                viewMenuItem(restaurantName, itemName);
            });

            itemElement.append(nameElement, button);
            menuDisplay.appendChild(itemElement);
        });

    } catch (error) {
        console.error("Error loading menu:", error);
        menuDisplay.textContent = `Could not load menu: ${error.message}`;
    }
}

// Display details for an individual menu item
async function viewMenuItem(restaurantName, menuItem) {
    const menuDisplay = document.getElementById("menu-display");

    try {
        const response = await fetch(
            `${API_URL}/restaurants/${encodeURIComponent(restaurantName)}/menu/${encodeURIComponent(menuItem)}`
        );

        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        }

        const item = await response.json();

        // Create elements safely
        const itemDetails = document.createElement("div");
        const heading = document.createElement("h4");

        heading.textContent = "Menu Item Details";

        const name = document.createElement("p");
        name.textContent = `Name: ${item.Name}`;

        const price = document.createElement("p");
        price.textContent = `Price: ${parseFloat(item.Price).toFixed(1)}`;

        const availability = document.createElement("p");
        availability.textContent = `Availability: ${item.Availability ? "True" : "False"}`;

        itemDetails.append(heading, name, price, availability);

        menuDisplay.appendChild(itemDetails);

    } catch (error) {
        console.error("Error loading menu item:", error);
        menuDisplay.textContent = "Could not load menu item details.";
    }
}

// Load restaurants into the management dropdown
async function loadManageRestaurants() {
    try {
        const response = await fetch(`${API_URL}/restaurants/`);

        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        }

        const restaurants = await response.json();

        // Keep the default option
        manageIdSelect.innerHTML =
            '<option value="">Select a restaurant</option>';

        restaurants.forEach((restaurant) => {
            const option = document.createElement("option");

            option.value = restaurant.Name;
            option.textContent = restaurant.Name;

            manageIdSelect.appendChild(option);
        });
    } catch (error) {
        console.error("Error loading restaurants:", error);
        formStatus.textContent =
            "Could not load restaurants. Please try again.";
    }
}

// Clear the form
function clearRestaurantForm() {
    restaurantForm.reset();
    selectedRestaurant = null;
}

// Change between Create and Update modes
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

// Initially disable the restaurant dropdown in Create mode
manageIdSelect.disabled = true;
manageIdSelect.required = false;

// Load selected restaurant details into the form

let selectedRestaurant = null;

// Load selected restaurant details into the form
manageIdSelect.addEventListener("change", async () => {
    const restaurantName = manageIdSelect.value;

    clearRestaurantForm();
    formStatus.textContent = "";

    if (!restaurantName) {
        return;
    }

    try {
        const response = await fetch(
            `${API_URL}/restaurants/${encodeURIComponent(restaurantName)}`
        );

        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        }

        const restaurant = await response.json();

        // Save the complete restaurant object
        selectedRestaurant = restaurant;

        document.getElementById("name").value =
            restaurant.Name ?? "";

        document.getElementById("cuisine").value =
            restaurant.Cuisine ?? "";

        document.getElementById("address").value =
            restaurant.Address ?? "";

        document.getElementById("hours").value =
            restaurant.Hours ?? "";

        document.getElementById("photos").value =
            (restaurant.Photos ?? []).join("\n");

    } catch (error) {
        console.error("Error loading restaurant:", error);
        formStatus.textContent =
            "Could not load restaurant details.";
    }
});


// Create or update a restaurant when the form is submitted
restaurantForm.addEventListener("submit", async (event) => {
    event.preventDefault();

   
const operation = operationSelect.value;
const restaurantName = manageIdSelect.value;

if (operation === "update" && !selectedRestaurant) {
    formStatus.textContent =
        "Please select a restaurant and wait for its details to load.";
    return;
}

const restaurantData = {
    id: selectedRestaurant.id,
    Name: document.getElementById("name").value.trim(),
    Cuisine: document.getElementById("cuisine").value.trim(),
    Address: document.getElementById("address").value.trim(),
    Hours: document.getElementById("hours").value.trim(),
    Photos: document.getElementById("photos").value
        .split("\n")
        .map(url => url.trim())
        .filter(url => url !== ""),
    menu: selectedRestaurant.menu ?? []
};

// Preserve existing fields when updating
if (operation === "update") {
    restaurantData.id = selectedRestaurant.id;
    restaurantData.menu = selectedRestaurant.menu ?? [];
}


    // Choose the correct endpoint and HTTP method
    const url = operation === "create"
        ? `${API_URL}/restaurants/`
        : `${API_URL}/restaurants/${encodeURIComponent(restaurantName)}`;

    const method = operation === "create" ? "POST" : "PUT";

    try {
        saveButton.disabled = true;
        saveButton.textContent = operation === "create"
            ? "Creating..."
            : "Updating...";

        const response = await fetch(url, {
            method: method,
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(restaurantData)
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(
                `HTTP ${response.status}: ${errorText}`
            );
        }

        formStatus.textContent = operation === "create"
            ? "Restaurant created successfully!"
            : "Restaurant updated successfully!";

        // Refresh the dropdown and restaurant list
        await loadManageRestaurants();

        if (typeof loadRestaurants === "function") {
            await loadRestaurants();
        }

        if (operation === "create") {
            clearRestaurantForm();
        }

    } catch (error) {
        console.error("Error saving restaurant:", error);
        formStatus.textContent =
            `Failed to save restaurant: ${error.message}`;
    } finally {
        saveButton.disabled = false;
        saveButton.textContent =
            operationSelect.value === "create"
                ? "Create Restaurant"
                : "Update Restaurant";
    }
});

// Load the dropdown when the page starts
loadManageRestaurants();

async function loadMenuRestaurants() {
    try {
        const response = await fetch(`${API_URL}/restaurants`);

        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        }

        allRestaurants = await response.json();

        restaurantSelect.innerHTML =
            '<option value="">Select a restaurant</option>';

        allRestaurants.forEach(restaurant => {
            const option = document.createElement("option");
            option.value = restaurant.Name;
            option.textContent = restaurant.Name;
            restaurantSelect.appendChild(option);
        });
    } catch (error) {
        console.error("Error loading restaurants:", error);
        statusMessage.textContent = "Could not load restaurants.";
    }
}

// Find the selected restaurant
function getSelectedRestaurant() {
    return allRestaurants.find(
        restaurant => restaurant.Name === restaurantSelect.value
    );
}

// Update the form based on the selected operation
function updateMenuForm() {
    const operation = menuOperationSelect ? menuOperationSelect.value : "create";
    const isUpdate = operation === "update";

    // Show/hide or enable/disable item selection dropdown
    itemSelect.style.display = isUpdate ? "block" : "none";
    itemSelect.required = isUpdate;

    if (menuSaveButton) {
        menuSaveButton.textContent = isUpdate
            ? "Update Menu Item"
            : "Add Menu Item";
    }

    // Clear old values when switching operations
    nameInput.value = "";
    priceInput.value = "";
    availabilitySelect.value = "true";
    statusMessage.textContent = "";

    loadMenuItems();
}

// Load menu items for the selected restaurant



async function loadMenuItems() {
    const restaurantName = restaurantSelect.value;

    itemSelect.innerHTML =
        '<option value="">Select a menu item</option>';

    if (!restaurantName) {
        return;
    }

    try {
        const response = await fetch(
            `${API_URL}/restaurants/${encodeURIComponent(restaurantName)}/menu`
        );

        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        }

        const menuItems = await response.json();
        currentMenuItems = menuItems;

        console.log("Menu items received from API:", menuItems);

        if (!Array.isArray(menuItems)) {
            throw new Error("The menu API did not return a list.");
        }

        menuItems.forEach((item, index) => {
            const option = document.createElement("option");

            // Index distinguishes items with duplicate names
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




// Fill the form when an item is selected for updating
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



// Create or update a menu item
async function saveMenuItem(event) {
    event.preventDefault();

    const restaurantName = restaurantSelect.value;
    
    const menuOperationSelect = document.getElementById("menu-operation");
    const operation = menuOperationSelect ? menuOperationSelect.value : "create";
    
    const selectedIndex = itemSelect.value;

const itemName =
    selectedIndex !== "" &&
    restaurantSelect.value
        ? getSelectedRestaurant()?.menu[Number(selectedIndex)]?.Name
        : "";

    const menuSaveButton = document.querySelector("#menu-form button[type='submit']") || saveButton;

    if (!restaurantName) {
        statusMessage.textContent = "Please select a restaurant.";
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

    // Construct the appropriate endpoint
    let url = `${API_URL}/restaurants/${encodeURIComponent(restaurantName)}/menu`;
    let method = "POST";

    if (operation === "update") {
        url += `/${encodeURIComponent(itemName)}`;
        method = "PUT";
    }

    try {
        menuSaveButton.disabled = true;
        statusMessage.textContent = "Saving menu item...";

        const response = await fetch(url, {
            method: method,
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(menuData)
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            let errorMessage;

            if (Array.isArray(errorData.detail)) {
                // FastAPI validation errors
                errorMessage = errorData.detail
                    .map(error => {
                        const field = Array.isArray(error.loc)
                            ? error.loc.join(" → ")
                            : "Unknown field";

                        return `${field}: ${error.msg}`;
                    })
                    .join("; ");
            } else if (typeof errorData.detail === "string") {
                errorMessage = errorData.detail;
            } else {
                errorMessage = JSON.stringify(errorData);
            }

            throw new Error(
                errorMessage || `HTTP error: ${response.status}`
            );
        }

        statusMessage.textContent = operation === "create"
            ? "Menu item added successfully!"
            : "Menu item updated successfully!";

        // Reload restaurant data so the dropdown and form use fresh data
        await loadMenuRestaurants();
        loadMenuItems();

        if (operation === "create") {
            menuForm.reset();
            availabilitySelect.value = "true";
        } else {
            // Keep the updated item selected
            itemSelect.value = itemName;
            selectMenuItem();
        }

    } catch (error) {
        console.error("Error saving menu item:", error);
        statusMessage.textContent = `Failed to save menu item: ${error.message}`;
    } finally {
        menuSaveButton.disabled = false;
    }
}

document.addEventListener("DOMContentLoaded", () => {
    loadRestaurants();

    document
        .getElementById("restaurant-search")
        .addEventListener("input", searchRestaurants);

    document
        .getElementById("cuisine-filter")
        .addEventListener("change", searchRestaurants);
        
    loadMenuRestaurants();
    updateMenuForm();

    document
        .getElementById("menu-restaurant-id")
        .addEventListener("change", loadMenuItems);

    if (menuOperationSelect) {
        menuOperationSelect.addEventListener("change", updateMenuForm);
    }

    document
        .getElementById("menu-item-id")
        .addEventListener("change", selectMenuItem);

    document
        .getElementById("menu-form")
        .addEventListener("submit", saveMenuItem);
});