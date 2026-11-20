import { API_URL } from "./config.js";
import { saveSession } from "./session.js";

const loginForm = document.getElementById("login-form");
const registrationForm = document.getElementById("owner-register-form");
const status = document.getElementById("login-status");

document
    .getElementById("show-registration")
    .addEventListener("click", () => {
        loginForm.hidden = true;
        registrationForm.hidden = false;
        status.textContent = "";
    });

document
    .getElementById("show-login")
    .addEventListener("click", () => {
        registrationForm.hidden = true;
        loginForm.hidden = false;
        status.textContent = "";
    });

registrationForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = new FormData(registrationForm);
    const submitButton = registrationForm.querySelector(
        "button[type='submit']"
    );
    const registration = {
        firstName: form.get("firstName").trim(),
        lastName: form.get("lastName").trim(),
        Address: form.get("Address").trim(),
        emailAddress: form.get("emailAddress").trim(),
        phoneNumber: form.get("phoneNumber").trim(),
        username: form.get("username").trim(),
        password: form.get("password"),
        restaurant: {
            Name: form.get("restaurantName").trim(),
            Cuisine: form.get("cuisine").trim(),
            Address: form.get("restaurantAddress").trim(),
            Hours: form.get("hours").trim(),
            Photos: [],
            menu: []
        }
    };
    submitButton.disabled = true;
    status.textContent = "Creating account...";

    try {
        const response = await fetch(
            `${API_URL}/restaurant-owners/register`,
            {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(registration)
            }
        );
        const result = await response.json();
        if (!response.ok) {
            const detail = result.detail;
            throw new Error(
                Array.isArray(detail)
                    ? detail.map(issue => issue.msg).join(", ")
                    : detail || "Could not create account."
            );
        }
        document.getElementById("username").value = registration.username;
        registrationForm.reset();
        registrationForm.hidden = true;
        loginForm.hidden = false;
        status.textContent = "Account created. Sign in to continue.";
    } catch (error) {
        console.error("Registration failed:", error);
        status.textContent = error.message;
    } finally {
        submitButton.disabled = false;
    }
});

document
    .getElementById("login-form")
    .addEventListener("submit", async (event) => {
        event.preventDefault();

        const username = document
            .getElementById("username")
            .value
            .trim();
        const password = document.getElementById("password").value;
        const submitButton = event.currentTarget.querySelector(
            "button[type='submit']"
        );

        status.textContent = "Checking account...";
        submitButton.disabled = true;

        try {
            let session = null;

            if (username !== "admin") {
                const customerResponse = await fetch(
                    `${API_URL}/customer/login`,
                    {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({ username, password })
                    }
                );

                if (customerResponse.ok) {
                    session = await customerResponse.json();
                } else if (customerResponse.status !== 401) {
                    throw new Error(
                        `Could not check customer account (HTTP ${customerResponse.status}).`
                    );
                }
            }

            if (!session && username !== "admin") {
                const ownerResponse = await fetch(
                    `${API_URL}/restaurant-owners/login`,
                    {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({ username, password })
                    }
                );

                if (ownerResponse.ok) {
                    session = await ownerResponse.json();
                } else if (ownerResponse.status !== 401) {
                    throw new Error(
                        `Could not check restaurant owner account (HTTP ${ownerResponse.status}).`
                    );
                }
            }

            if (!session && username === "admin" && password === "admin") {
                session = { username, role: "admin" };
            }

            if (!session) {
                status.textContent = "Incorrect username or password.";
                return;
            }

            saveSession(session);
            window.location.replace("index.html");
        } catch (error) {
            console.error("Sign-in failed:", error);
            status.textContent = error.message;
        } finally {
            submitButton.disabled = false;
        }
    });
