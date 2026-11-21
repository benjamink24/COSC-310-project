
# Food-Delivery Application

## Team Name: πthon

### Required Python Version

Python 3.10+

### Setup Instructions

Clone the repository:
```bash
git clone <https://github.com/benjamink24/COSC-310-project>

cd project-root

### Virtual-environment Instructions

```bash
python -m venv .venv
.venv\Scripts\activate

### Dependency Installations

pip install -r requirements.txt

### How to start the application

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

### Open a new terminal window

cd project-root

```bash
 python -m http.server 5500 --directory frontend

 ### open http://127.0.0.1:5500/

### API Endpoint Paths

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Checks whether the application is running |
| POST | `/restaurant-owners/register` | Creates a restaurant owner account and its associated restaurant |
| POST | `/restaurant-owners/login` | Authenticates an owner and returns a one-hour bearer session |
| GET | `/restaurant-owners/me` | Returns the authenticated owner and associated restaurant |
| POST | `/restaurant-owners/logout` | Revokes the authenticated owner session |
| POST | `/restaurant-owners/deactivate` | Deactivates the authenticated owner and removes their restaurant from normal use |
| GET | `/restaurants` | Returns available restaurants |
| GET | `/docs` | Returns documentation |
| POST | `/restaurants` | Returns a new created restaurant |
| PUT | `/restaurants/{rest_name}` | Returns updated restaurant |
| POST | `/restaurants/{res_name}/menu` | Returns a new created menu item |
| PUT | `/restaurants/{res_name}/menu{item_name}` | Returns updated menu item |
| GET | `/restaurants/{restaurant_name}` | Returns restaurant details |
| GET | `/restaurants/{restaurant_name}/menu` | Returns restaurant menu |
| GET | `/restaurants/{restaurant_name}/menu/{menu_item}` | Returns one menu item |
| GET | `/restaurants/filter/{cuisine_type}` | Returns filtered restaurants by cuisine |
| POST | `/customer/sign-up` | Creates a customer account |
| POST | `/customer/login` | Authenticates a customer and returns a bearer session |
| GET | `/customer/me` | Returns the authenticated customer's profile |
| PUT | `/customer/me` | Updates the authenticated customer's profile |
| POST | `/customer/logout` | Revokes the authenticated customer session |
| POST | `/customer/deactivate` | Deactivates the authenticated customer account |
| GET | `/cart/me` | Returns the authenticated customer's cart and total, or 404 when they have no cart |
| POST | `/cart/me/items` | Adds a menu item to the authenticated customer's cart |
| PUT | `/cart/me/items/{item_name}` | Sets the quantity of a cart item |
| DELETE | `/cart/me/items/{item_name}` | Removes one item from the cart |
| DELETE | `/cart/me` | Deletes the authenticated customer's cart |
| POST | `/checkout/` | Turns the cart into an order and empties the cart |
| GET | `/checkout/history/me` | Lists the authenticated customer's past orders, oldest first |


### /docs Path
Interactive Swagger API documentation is available at:

http://127.0.0.1:8000/docs

### Location of Representative Data

project-root\data\restaurants.json
Restaurant owner accounts are persisted in `project-root\data\restaurant_owners.json`.
Owner and customer passwords are stored as salted PBKDF2 hashes. Restaurant updates, menu changes, cart, checkout, and customer profile routes require the bearer token returned by login. Sessions are held in memory and expire after one hour.

### How to run Tests

```bash
pytest

### Brief Repository Structure
project-root/
├── app/
│   ├── api/
│   │   └── routes/
│   ├── services/
│   ├── repositories/
│   ├── schemas/
│   ├── main.py
│   └── frontend/
├── data/
│   └── restaurants.json
├── tests/
├── scrum/
│   └── team-agreement.md
├── .gitignore
├── requirements.txt 
└── README.md