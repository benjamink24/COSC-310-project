
const SESSION_KEY = "manharEatsSession";

function readCurrentUser() {
    const storedSession = sessionStorage.getItem(SESSION_KEY);

    if (!storedSession) {
        return null;
    }

    let session;
    try {
        session = JSON.parse(storedSession);
    } catch (error) {
        sessionStorage.removeItem(SESSION_KEY);
        return null;
    }

    if (!session || !["customer", "restaurant", "admin"].includes(session.role)) {
        sessionStorage.removeItem(SESSION_KEY);
        return null;
    }

    return session;
}

const currentUser = readCurrentUser();

function isRestaurantUser() {
    return Boolean(currentUser && currentUser.role === "restaurant");
}

function isCustomerUser() {
    return Boolean(currentUser && currentUser.role === "customer");
}

function canManageRestaurantEndpoints() {
    return Boolean(
        currentUser &&
        ["restaurant", "admin"].includes(currentUser.role)
    );
}

function canManageRestaurant(restaurantId) {
    return Boolean(
        currentUser &&
        currentUser.role === "restaurant" &&
        String(restaurantId) === String(currentUser.restaurantId)
    );
}

function canViewRestaurant(restaurantId) {
    return Boolean(
        currentUser &&
        (["customer", "admin"].includes(currentUser.role) ||
        canManageRestaurant(restaurantId)
        )
    );
}

if (!currentUser) {
    window.location.replace("login.html");
} else {
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

document.getElementById("logout-button").addEventListener("click", () => {
    sessionStorage.removeItem(SESSION_KEY);
    window.location.replace("login.html");
});

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
let currentMenuItems = [];

const createRestaurantOption = operationSelect.querySelector(
    'option[value="create"]'
);
const updateRestaurantOption = operationSelect.querySelector(
    'option[value="update"]'
);
const manageIdLabel = document.getElementById("manage-id-label");

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

function visibleRestaurants(restaurants) {
    if (!currentUser || currentUser.role !== "restaurant") {
        return restaurants;
    }

    return restaurants.filter(
        restaurant => String(restaurant.id) === String(currentUser.restaurantId)
    );
}

async function loadCustomerProfile() {
    if (!isCustomerUser()) {
        return;
    }

    const status = document.getElementById("customer-status");
    const profile = document.getElementById("customer-profile");
    const customerId = Number(currentUser.customerId);

    if (!Number.isInteger(customerId) || customerId < 1) {
        status.textContent = "This customer login has no linked customer profile.";
        return;
    }

    status.textContent = "Loading your customer profile...";

    try {
        const response = await fetch(`${API_URL}/customer/${customerId}`);

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
    } catch (error) {
        console.error("Error loading customer profile:", error);
        status.textContent =
            `Could not load your customer profile: ${error.message}`;
    }
}

// GET /restaurants/ - List Restaurants
async function loadRestaurants() {
    if (!currentUser) {
        return;
    }

    const status = document.getElementById("status");

    status.textContent = "Loading restaurants...";

    try {
        const response = await fetch(`${API_URL}/restaurants/`);

        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        }

        allRestaurants = await response.json();
        const availableRestaurants = visibleRestaurants(allRestaurants);

        populateCuisineFilter(availableRestaurants);
        displayRestaurants(availableRestaurants);
        
        status.textContent =
            `Found ${availableRestaurants.length} restaurant(s).`;

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
            viewRestaurantDetails(restaurant.id);
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
    const filteredRestaurants = visibleRestaurants(allRestaurants).filter(restaurant => {
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
function populateCuisineFilter(restaurants = visibleRestaurants(allRestaurants)) {
    const cuisineFilter = document.getElementById("cuisine-filter");

    cuisineFilter.innerHTML = "";

    const defaultOption = document.createElement("option");
    defaultOption.value = "";
    defaultOption.textContent = "All Cuisines";
    cuisineFilter.appendChild(defaultOption);

    const cuisines = [
        ...new Set(
            restaurants
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
async function viewRestaurantDetails(restaurantId) {
    if (!canViewRestaurant(restaurantId)) {
        return;
    }

    const details = document.getElementById("restaurant-details");

    details.textContent = "Loading restaurant details...";

    try {
        const response = await fetch(
            `${API_URL}/restaurants/${encodeURIComponent(restaurantId)}`
        );

        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        }

        const restaurant = await response.json();

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
                viewRestaurantMenu(restaurantId);
            });

    } catch (error) {
        console.error("Error loading restaurant details:", error);
        details.textContent = "Could not load restaurant details.";
    }
}

// Display all menu items for the selected restaurant
async function viewRestaurantMenu(restaurantId) {
    if (!canViewRestaurant(restaurantId)) {
        return;
    }

    const menuDisplay = document.getElementById("menu-display");

    menuDisplay.textContent = "Loading menu...";

    try {
        const url =
            `${API_URL}/restaurants/${encodeURIComponent(restaurantId)}/menu`;


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
                viewMenuItem(restaurantId, itemName);
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
async function viewMenuItem(restaurantId, menuItem) {
    if (!canViewRestaurant(restaurantId)) {
        return;
    }

    const menuDisplay = document.getElementById("menu-display");

    try {
        const response = await fetch(
            `${API_URL}/restaurants/${encodeURIComponent(restaurantId)}/menu/${encodeURIComponent(menuItem)}`
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
        price.textContent = `Price: ${Number(item.Price).toFixed(2)}`;

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
    if (!isRestaurantUser()) {
        return;
    }

    try {
        const response = await fetch(`${API_URL}/restaurants/`);

        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        }

        const restaurants = await response.json();

        // Keep the default option
        manageIdSelect.innerHTML =
            '<option value="">Select a restaurant</option>';

        const manageableRestaurants = restaurants.filter(
            restaurant => canManageRestaurant(restaurant.id)
        );

        manageableRestaurants.forEach((restaurant) => {
            const option = document.createElement("option");

            option.value = String(restaurant.id);
            option.textContent = restaurant.Name;

            manageIdSelect.appendChild(option);
        });

        if (manageableRestaurants.length === 0) {
            formStatus.textContent =
                "No restaurant is assigned to this login.";
            return;
        }

        manageIdSelect.value = String(currentUser.restaurantId);
        await loadSelectedRestaurant();
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
            fetch(`${API_URL}/restaurants/${encodeURIComponent(restaurantId)}`),
            fetch(`${API_URL}/restaurants/${encodeURIComponent(restaurantId)}/menu`)
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
}

manageIdSelect.addEventListener("change", loadSelectedRestaurant);


// Create or update a restaurant when the form is submitted
restaurantForm.addEventListener("submit", async (event) => {
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

    // Choose the correct endpoint and HTTP method
    const url = operation === "create"
        ? `${API_URL}/restaurants/`
        : `${API_URL}/restaurants/${encodeURIComponent(restaurantId)}`;

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
        await loadMenuRestaurants();

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

async function loadMenuRestaurants() {
    if (!isRestaurantUser()) {
        return;
    }

    try {
        const response = await fetch(`${API_URL}/restaurants`);

        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        }

        allRestaurants = await response.json();

        restaurantSelect.innerHTML =
            '<option value="">Select a restaurant</option>';

        const manageableRestaurants = allRestaurants.filter(
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

// Find the selected restaurant
function getSelectedRestaurant() {
    return allRestaurants.find(
        restaurant => String(restaurant.id) === restaurantSelect.value
    );
}

// Update the form based on the selected operation
function updateMenuForm() {
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

// Load menu items for the selected restaurant
async function loadMenuItems() {
    if (!isRestaurantUser()) {
        return;
    }

    const restaurantId = restaurantSelect.value;

    itemSelect.innerHTML =
        '<option value="">Select a menu item</option>';

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
            `${API_URL}/restaurants/${encodeURIComponent(restaurantId)}/menu`
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

    if (!isRestaurantUser()) {
        return;
    }

    const restaurantId = restaurantSelect.value;
    
    const menuOperationSelect = document.getElementById("menu-operation");
    const operation = menuOperationSelect ? menuOperationSelect.value : "create";
    
    const selectedIndex = itemSelect.value;

    const itemName =
        selectedIndex !== "" &&
        currentMenuItems &&
        currentMenuItems[Number(selectedIndex)]
            ? currentMenuItems[Number(selectedIndex)].Name
            : "";

    const menuSaveButton = document.querySelector("#menu-form button[type='submit']") || saveButton;

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

    let url = `${API_URL}/restaurants/${encodeURIComponent(restaurantId)}/menu`;
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

        // Reload the menu items dropdown with fresh server data
        await loadMenuItems();

        if (operation === "create") {
            menuForm.reset();
            availabilitySelect.value = "true";
        }

    } catch (error) {
        console.error("Error saving menu item:", error);
        statusMessage.textContent = `Failed to save menu item: ${error.message}`;
    } finally {
        menuSaveButton.disabled = false;
    }
}

document.addEventListener("DOMContentLoaded", () => {
    if (!currentUser) {
        return;
    }

    if (currentUser.role === "customer") {
        loadCustomerProfile();
    }

    loadRestaurants();

    document
        .getElementById("restaurant-search")
        .addEventListener("input", searchRestaurants);

    document
        .getElementById("cuisine-filter")
        .addEventListener("change", searchRestaurants);
        
    if (isRestaurantUser()) {
        loadManageRestaurants();
        loadMenuRestaurants();
        updateMenuForm();
    }

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