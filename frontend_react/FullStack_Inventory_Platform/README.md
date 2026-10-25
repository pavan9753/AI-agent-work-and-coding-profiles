# Stockroom — Full-Stack Inventory Operations

A recruiter-ready full-stack sample: a React operations dashboard backed by a layered Java / Spring Boot REST API and an H2 database. The UI supports catalog search, category and stock filters, product create/edit/delete, low-stock alerts, CSV export, and live summary metrics.

## Stack and architecture

- **Frontend:** React 19, Vite, Lucide, responsive CSS
- **Backend:** Java 21, Spring Boot 4.1, Spring Web, Bean Validation, Spring Data JPA
- **Database:** H2 in-memory database with demo records seeded at startup
- **API shape:** JSON REST endpoints under `/api`; UUID identifiers; validation and consistent error responses

```text
frontend/                         React inventory dashboard
backend/src/main/java/com/pavan/inventory/
  api/                            REST controller and request/response records
  domain/                         JPA entity and demo data
  repository/                     Spring Data repository
  service/                        Business rules and dashboard aggregation
  web/                            API validation/error response handling
```

## Run locally

Prerequisites: Java 21, Maven 3.6.3+, and Node.js 18+ with npm.

### 1. Start the API

In a terminal:

```powershell
cd frontend_react/FullStack_Inventory_Platform/backend
mvn spring-boot:run
```

The REST API is at `http://localhost:8080`. The in-memory database is seeded with six fictional products. The optional local H2 console is at `http://localhost:8080/h2-console` with JDBC URL `jdbc:h2:mem:inventory`, username `sa`, and an empty password.

### 2. Start the React app

Open another terminal at the repository root:

```powershell
cd frontend_react/FullStack_Inventory_Platform/frontend
npm install
npm run dev
```

Open the local URL printed by Vite (normally `http://localhost:5173`). Keep the API process running. To point the UI at a different API, create `frontend/.env.local` with `VITE_API_URL=http://localhost:8080/api`.

For macOS or Linux, the same commands work with `cd frontend_react/FullStack_Inventory_Platform/backend` and `cd frontend_react/FullStack_Inventory_Platform/frontend` in two terminals.

## API overview

| Method | Route | Purpose |
| --- | --- | --- |
| `GET` | `/api/dashboard` | Product count, low-stock count, units, and inventory value |
| `GET` | `/api/items?q=keyboard` | List/search by product name, SKU, or category |
| `GET` | `/api/items/{id}` | Fetch one product |
| `POST` | `/api/items` | Create a product; validates fields and enforces unique SKU |
| `PUT` | `/api/items/{id}` | Update a product |
| `DELETE` | `/api/items/{id}` | Remove a product |

Example request:

```json
{
  "name": "USB-C dock",
  "sku": "ACC-118",
  "category": "Accessories",
  "unitPrice": 129.00,
  "quantity": 7,
  "reorderThreshold": 10
}
```

## Engineering notes

- The service layer owns SKU uniqueness checks, not-found handling, and the summary calculations.
- Request records validate user input at the API boundary; the UI also shows request failures and loading states.
- CORS is restricted to the local Vite origin by default. Set `FRONTEND_ORIGIN` when running the UI from another origin.
- The database is deliberately in-memory so a clean run is easy; changes disappear when the backend stops. This is a demo, not an authenticated production inventory system.
- Prices are illustrative USD values. Seeded products and organization details are fictional.

## Source

[Project folder in this repository](https://github.com/pavan9753/AI-agent-work-and-coding-profiles/tree/main/frontend_react/FullStack_Inventory_Platform)
