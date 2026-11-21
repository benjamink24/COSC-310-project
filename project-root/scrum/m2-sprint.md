Scrum Sprint Planning Meeting Notes
Sprint Goal: Deliver a fully integrated, end-to-end customer workflow (Customer -> Restaurant -> Menu -> Cart -> Checkout -> Order)
Date: November 4th, 2026
Attendees: Benjamin Kelly, Manhar Khurana, Kai Maleniza, Maksym Pagette
Target Release Tag: m2-integrated-system

Sprint backlog & Task breakdown:

Epic 1: Shopping Cart
Owner: Kai & Makysm
- Implement active cart creation/retrieval for authenticated customers (enforce max one active cart per customer).

- Implement add item, update item quantity, remove item, clear cart, and retrieve cart contents.

- Implement authoritative backend subtotal and total calculation.

- Connect frontend cart UI (add/update/remove items and display backend-calculated totals).

- Add tests

Epic 2: Manage Customer Account
Owner: Ben & Manhar

- Implement customer registration, sign-in, profile retrieval, and profile/delivery address updates.

- Implement customer account deactivation (soft-delete/status toggle preserving historical IDs).

- Integrate authentication middleware/dependencies to identify logged-in customers and return proper 401/403 errors on unauthorized requests.

- Connect frontend registration, sign-in, and profile views to customer API endpoints.

- Add tests

Epic 3: Manage Restaurant Owner Accounts
Owner: Ben & Manhar
Functional Tasks:

- Implement restaurant owner registration/sign-in and role-based authorization protecting restaurant and menu mutation endpoints (401/403 for unauthenticated users or customer roles).

- Ensure all M1 restaurant/menu endpoints remain integrated: search/filter restaurants, retrieve details, browse menus, create/update restaurants, add/update menu items, and toggle item availability/deactivation.

- Verify stable restaurant and menu item IDs across restarts.

- Connect frontend restaurant/menu browsing (and owner management views, if applicable) to REST API.

- Add tests

Epic 4: Checkout and Order Management
Owner: Kai & Maksym
Implement Checkout orchestration workflow in exact sequence:

- Validate active customer state, restaurant, cart non-emptiness, item quantities, and cross-subsystem rules.

- Revalidate current menu-item availability and current prices via Menu/Restaurant interfaces.

- Recalculate authoritative subtotal and total on the backend.

- Create and persist the Order with historical snapshot data (items, prices at purchase, customer/restaurant IDs).

- Clear or close the active cart only after order persistence succeeds.

- Return the created order.

- Implement endpoints to retrieve an individual order and all orders for an authenticated customer.

- Connect frontend checkout trigger and order confirmation/history view to REST API.

- Add tests

Team Workflow:
- Every task starts from a Github Issue with clear acceptance criteria linked on the project board.
- No self-approvals
- Every PR requires peer review before merging to main

Definition of Done:
- Code merged via reviewed PR with passing CI
- Cross-subsystem rules enforced on the backend
- OpenAPI schemas.status codes accurate
- Evidence logged for Decision Receipts (PR link + test/review reference)