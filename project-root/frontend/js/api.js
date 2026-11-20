import { API_URL } from "./config.js";

export function apiUrl(path) {
    return `${API_URL}${path}`;
}

export async function errorMessageFromResponse(response) {
    const raw = await response.text();
    if (!raw) {
        return `HTTP error: ${response.status}`;
    }

    try {
        const errorData = JSON.parse(raw);
        if (Array.isArray(errorData.detail)) {
            return errorData.detail
                .map(error => {
                    const field = Array.isArray(error.loc)
                        ? error.loc.join(" → ")
                        : "Unknown field";
                    return `${field}: ${error.msg}`;
                })
                .join("; ");
        }
        if (typeof errorData.detail === "string") {
            return errorData.detail;
        }
        return JSON.stringify(errorData);
    } catch (error) {
        return raw;
    }
}
