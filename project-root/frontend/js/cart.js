import { apiUrl, errorMessageFromResponse } from "./api.js";
import { authHeaders, linkedCustomerId } from "./session.js";

let activeCustomerId = null;

function cartStatus(message) {
    const status = document.getElementById("cart-status");
    if (status) {
        status.textContent = message;
    }
}

function checkoutStatus(message) {
    const status = document.getElementById("checkout-status");
    if (status) {
        status.textContent = message;
    }
}

function historyStatus(message) {
    const status = document.getElementById("history-status");
    if (status) {
        status.textContent = message;
    }
}

function renderCart(cart) {
    const lines = document.getElementById("cart-lines");
    const total = document.getElementById("cart-total");
    const clearButton = document.getElementById("clear-cart-button");
    const checkoutButton = document.querySelector("#checkout-form button[type='submit']");
    lines.replaceChildren();

    const items = cart && Array.isArray(cart.items) ? cart.items : [];
    if (!cart || items.length === 0) {
        lines.textContent = "Your cart is empty.";
        total.textContent = cart ? `Total: $${Number(cart.total).toFixed(2)}` : "";
        clearButton.hidden = !cart;
        if (checkoutButton) {
            checkoutButton.disabled = true;
        }
        return;
    }

    items.forEach(item => {
        const row = document.createElement("div");
        row.className = "cart-line";

        const name = document.createElement("span");
        name.className = "line-name";
        name.textContent = item.Name;

        const price = document.createElement("span");
        price.textContent = `$${Number(item.Price).toFixed(2)}`;

        const quantity = document.createElement("input");
        quantity.type = "number";
        quantity.min = "1";
        quantity.step = "1";
        quantity.value = String(item.quantity);
        quantity.setAttribute("aria-label", `Quantity for ${item.Name}`);
        quantity.addEventListener("change", () => {
            updateQuantity(item.Name, quantity.value);
        });

        const removeButton = document.createElement("button");
        removeButton.type = "button";
        removeButton.textContent = "Remove";
        removeButton.addEventListener("click", () => {
            removeItem(item.Name);
        });

        row.append(name, price, quantity, removeButton);
        lines.appendChild(row);
    });

    total.textContent = `Total: $${Number(cart.total).toFixed(2)}`;
    clearButton.hidden = false;
    if (checkoutButton) {
        checkoutButton.disabled = false;
    }
}

function renderHistory(orders) {
    const history = document.getElementById("order-history");
    history.replaceChildren();

    if (!Array.isArray(orders) || orders.length === 0) {
        history.textContent = "You have no past orders.";
        historyStatus("");
        return;
    }

    orders.forEach(order => {
        const card = document.createElement("article");
        card.className = "order-card";

        const heading = document.createElement("h4");
        heading.textContent = `Order ${order.orderId}`;

        const meta = document.createElement("p");
        meta.textContent =
            `${order.timestamp ?? ""} · ${order.status ?? "placed"} · ` +
            `${order.paymentMethod ?? ""} · $${Number(order.total).toFixed(2)}`;

        card.append(heading, meta);

        (order.items ?? []).forEach(item => {
            const line = document.createElement("p");
            line.textContent =
                `${item.quantity} × ${item.Name} ($${Number(item.Price).toFixed(2)})`;
            card.appendChild(line);
        });

        history.appendChild(card);
    });

    historyStatus(`Loaded ${orders.length} order(s).`);
}

async function loadCart() {
    const response = await fetch(apiUrl("/cart/me"), {
        headers: authHeaders()
    });
    if (response.status === 404) {
        const message = await errorMessageFromResponse(response);
        if (message.toLowerCase().includes("cart")) {
            renderCart(null);
            cartStatus("Your cart is empty.");
            return;
        }
        throw new Error(message);
    }
    if (!response.ok) {
        throw new Error(await errorMessageFromResponse(response));
    }
    renderCart(await response.json());
    cartStatus("");
}

async function loadHistory() {
    const response = await fetch(apiUrl("/checkout/history/me"), {
        headers: authHeaders()
    });
    if (!response.ok) {
        throw new Error(await errorMessageFromResponse(response));
    }
    renderHistory(await response.json());
}

async function updateQuantity(itemName, rawQuantity) {
    const quantity = Number(rawQuantity);
    if (!Number.isInteger(quantity) || quantity < 1) {
        cartStatus("Quantity must be a whole number of at least 1.");
        await loadCart();
        return;
    }

    cartStatus("Updating quantity...");
    try {
        const response = await fetch(
            apiUrl(`/cart/me/items/${encodeURIComponent(itemName)}`),
            {
                method: "PUT",
                headers: authHeaders({ "Content-Type": "application/json" }),
                body: JSON.stringify({ quantity })
            }
        );
        if (!response.ok) {
            throw new Error(await errorMessageFromResponse(response));
        }
        renderCart(await response.json());
        cartStatus("Quantity updated.");
    } catch (error) {
        console.error("Error updating cart item:", error);
        cartStatus(error.message);
        await loadCart().catch(() => {});
    }
}

async function removeItem(itemName) {
    cartStatus("Removing item...");
    try {
        const response = await fetch(
            apiUrl(`/cart/me/items/${encodeURIComponent(itemName)}`),
            { method: "DELETE", headers: authHeaders() }
        );
        if (!response.ok) {
            throw new Error(await errorMessageFromResponse(response));
        }
        renderCart(await response.json());
        cartStatus("Item removed.");
    } catch (error) {
        console.error("Error removing cart item:", error);
        cartStatus(error.message);
    }
}

async function clearCart() {
    cartStatus("Clearing cart...");
    try {
        const response = await fetch(apiUrl("/cart/me"), {
            method: "DELETE",
            headers: authHeaders()
        });
        if (response.status === 404) {
            renderCart(null);
            cartStatus("Your cart is empty.");
            return;
        }
        if (!response.ok) {
            throw new Error(await errorMessageFromResponse(response));
        }
        renderCart(null);
        cartStatus("Cart cleared.");
    } catch (error) {
        console.error("Error clearing cart:", error);
        cartStatus(error.message);
    }
}

async function placeOrder(event) {
    event.preventDefault();
    const paymentMethod = document.getElementById("payment-method").value.trim();
    const submitButton = event.currentTarget.querySelector("button[type='submit']");
    if (!paymentMethod) {
        checkoutStatus("Enter a payment method.");
        return;
    }

    submitButton.disabled = true;
    checkoutStatus("Placing order...");
    try {
        const response = await fetch(apiUrl("/checkout/"), {
            method: "POST",
            headers: authHeaders({ "Content-Type": "application/json" }),
            body: JSON.stringify({
                cId: activeCustomerId,
                paymentMethod
            })
        });
        if (!response.ok) {
            throw new Error(await errorMessageFromResponse(response));
        }
        const order = await response.json();
        checkoutStatus(`Order ${order.orderId} placed.`);
        await loadCart();
        await loadHistory();
    } catch (error) {
        console.error("Error checking out:", error);
        checkoutStatus(error.message);
    } finally {
        const items = document.querySelectorAll("#cart-lines .cart-line");
        submitButton.disabled = items.length === 0;
    }
}

export async function startCart(customerId) {
    activeCustomerId = customerId;
    document.getElementById("clear-cart-button").addEventListener("click", clearCart);
    document.getElementById("checkout-form").addEventListener("submit", placeOrder);

    try {
        await loadCart();
    } catch (error) {
        console.error("Error loading cart:", error);
        cartStatus(`Could not load your cart: ${error.message}`);
    }

    try {
        await loadHistory();
    } catch (error) {
        console.error("Error loading order history:", error);
        historyStatus(`Could not load order history: ${error.message}`);
    }
}

export function showCartUnavailable() {
    cartStatus("This customer login has no linked customer profile.");
    historyStatus("This customer login has no linked customer profile.");
    const checkoutButton = document.querySelector("#checkout-form button[type='submit']");
    const clearButton = document.getElementById("clear-cart-button");
    if (checkoutButton) {
        checkoutButton.disabled = true;
    }
    if (clearButton) {
        clearButton.hidden = true;
    }
}

export async function addToCart(restaurantId, itemName) {
    const customerId = activeCustomerId ?? linkedCustomerId();
    if (customerId === null) {
        cartStatus("This customer login has no linked customer profile.");
        return;
    }

    cartStatus(`Adding ${itemName}...`);
    try {
        const response = await fetch(apiUrl("/cart/me/items"), {
            method: "POST",
            headers: authHeaders({ "Content-Type": "application/json" }),
            body: JSON.stringify({
                restaurantId: Number(restaurantId),
                Name: itemName,
                quantity: 1
            })
        });
        if (!response.ok) {
            throw new Error(await errorMessageFromResponse(response));
        }
        activeCustomerId = customerId;
        renderCart(await response.json());
        cartStatus(`Added ${itemName}.`);
    } catch (error) {
        console.error("Error adding cart item:", error);
        cartStatus(error.message);
    }
}
