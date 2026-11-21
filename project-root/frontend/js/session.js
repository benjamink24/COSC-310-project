import { SESSION_KEY } from "./config.js";

export function readCurrentUser() {
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

export const currentUser = readCurrentUser();

export function isRestaurantUser() {
    return Boolean(currentUser && currentUser.role === "restaurant");
}

export function isCustomerUser() {
    return Boolean(currentUser && currentUser.role === "customer");
}

export function canManageRestaurantEndpoints() {
    return Boolean(
        currentUser &&
        ["restaurant", "admin"].includes(currentUser.role)
    );
}

export function canManageRestaurant(restaurantId) {
    return Boolean(
        currentUser &&
        currentUser.role === "restaurant" &&
        String(restaurantId) === String(currentUser.restaurantId)
    );
}

export function canViewRestaurant(restaurantId) {
    return Boolean(
        currentUser &&
        (["customer", "admin"].includes(currentUser.role) ||
        canManageRestaurant(restaurantId)
        )
    );
}

export function linkedCustomerId() {
    if (!currentUser || currentUser.role !== "customer" || !currentUser.accessToken) {
        return null;
    }
    const customerId = Number(currentUser.cId ?? currentUser.customerId);
    if (!Number.isInteger(customerId) || customerId < 1) {
        return null;
    }
    return customerId;
}

export function authHeaders(headers = {}) {
    if (currentUser && currentUser.accessToken) {
        headers.Authorization = `Bearer ${currentUser.accessToken}`;
    }
    return headers;
}

export function ownerAuthHeaders(headers = {}) {
    return authHeaders(headers);
}

export function saveSession(session) {
    sessionStorage.setItem(SESSION_KEY, JSON.stringify(session));
}

export function clearSession() {
    sessionStorage.removeItem(SESSION_KEY);
}
