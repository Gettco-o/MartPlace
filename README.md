# MartPlace

MartPlace is a multi-tenant marketplace backend built for buyers, tenant vendors, and platform administrators. It provides authentication, tenant onboarding, product and inventory management, cart and checkout flows, wallet-based transactions, a full order lifecycle, and event-driven email notifications.

## Highlights

- Multi-tenant commerce architecture
- Buyer, tenant admin, tenant staff, and platform admin roles
- Product catalog and stock management
- Cart management and checkout
- Wallet credit/debit flows for buyers
- Tenant wallet crediting on completed sales
- Order lifecycle handling:
  - create
  - processing
  - fulfilled
  - delivered
  - cancelled
  - refunded
- Event-driven logging and notifications
- Buyer and tenant-admin email notifications
- Idempotent order creation and refund flows

## Tech Stack

- Python
- Quart
- Quart Schema
- SQLAlchemy 2.x
- Alembic
- SQLite with `aiosqlite` for local development
- PostgreSQL-ready via `asyncpg`

## Core Domain

MartPlace models a marketplace where:

- buyers can register, authenticate, fund wallets, browse products, add items to carts, and place orders
- tenant admins can create and manage products, process tenant orders, and view tenant wallet balances
- tenant staff can operate within a tenant under role restrictions
- platform admins can oversee tenants and platform-wide operations

## Features

### Authentication and Access Control

- buyer registration
- tenant user registration
- login, refresh token, and logout flows
- role-aware access checks across use cases

### Tenant Management

- create tenants
- optionally create the initial tenant admin during tenant creation
- list active tenants
- suspend and activate tenants

### Product Management

- create products per tenant
- update product price and stock
- list marketplace-wide products
- list tenant-specific products

### Cart and Checkout

- add items to cart
- remove items from cart
- list carts
- checkout cart into one or more orders

### Orders

- create orders
- list tenant orders
- cancel orders
- move orders to processing
- fulfill orders
- deliver orders
- refund orders

### Wallets

- credit buyer wallet
- debit buyer wallet
- list wallets
- get tenant wallet

### Events and Notifications

- domain events emitted from key business operations
- audit logging
- file-based event logging
- buyer email notifications for order updates
- tenant-admin email notifications for key order events
- user onboarding emails for buyers and tenant users

## Current Notification Behavior

MartPlace currently supports email notifications through event handlers.

### Buyer Emails

Buyers receive emails for:

- order created
- order processing started
- order fulfilled
- order delivered
- order cancelled
- order refunded
- order failed

### Tenant Admin Emails

Tenant admins receive emails for:

- new order created
- order cancelled
- order refunded
- order delivered

Email delivery is currently implemented with a file-backed email service for development, which writes messages to `logs/emails.log`.

## Project Structure

```text
app/
  domain/            # Entities, domain events, value objects, exceptions
  interfaces/        # Contracts for repositories, email service, event bus
  use_cases/         # Application business logic
  infrastructure/
    db/              # SQLAlchemy models, mappers, repositories, DB config
    event_handlers/  # Audit, logging, buyer emails, tenant emails, user emails
    services/        # File email service
    web/             # Quart app, routes, auth, schemas, dependencies
migrations/          # Alembic migrations
tests/               # Unit and integration-style tests
main.py              # App entrypoint and admin bootstrap command
```

## Architecture Notes

The codebase follows a layered architecture:

- `domain`: pure business rules and events
- `use_cases`: orchestration of business actions
- `interfaces`: abstractions for infrastructure dependencies
- `infrastructure`: database, web, event bus, and email implementations

This keeps business logic decoupled from transport and persistence concerns, and makes event-driven extensions easier to add over time.

## Getting Started

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd MartPlace
```

### 2. Create and Activate a Virtual Environment

```bash
python3 -m venv env
source env/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
pip install pytest
```

### 4. Configure Environment Variables

Create a `.env` file from the example:

Example values:

```env
QUART_ENV=development
QUART_DEBUG=true
DATABASE_URL=sqlite+aiosqlite:///marketplace.db
SQLALCHEMY_ECHO=false
SECRET_KEY=big-secret
AUTH_TOKEN_MAX_AGE=600
AUTH_REFRESH_TOKEN_MAX_AGE=302400
```

### 5. Run Database Migrations

```bash
alembic upgrade head
```

### 6. Start the API

```bash
python3 main.py serve --debug
```

The app also starts with:

```bash
python3 main.py
```

## Bootstrap the Initial Platform Admin

To create the first platform admin:

```bash
python3 main.py bootstrap-admin --email admin@example.com --name "Platform Admin" --password "strong-password"
```

If any field is omitted, the command prompts for it interactively.

## API Overview

### Auth

- `POST /auth/login`
- `POST /auth/refresh`
- `POST /auth/logout`

### Users

- `POST /users/buyers`
- `POST /users/tenant-users`
- `GET /users/<user_id>`
- `GET /users/`

### Tenants

- `GET /tenants/active`
- `POST /tenants/`
- `GET /tenants/`
- `GET /tenants/<tenant_id>`
- `PATCH /tenants/<tenant_id>/suspend`
- `PATCH /tenants/<tenant_id>/activate`

### Products

- `GET /products/`
- `POST /products/`
- `GET /products/<tenant_id>`
- `GET /products/<tenant_id>/<product_id>`
- `PATCH /products/<tenant_id>/<product_id>/update`

### Cart

- `GET /cart/`
- `POST /cart/items`
- `DELETE /cart/items`
- `POST /cart/checkout`

### Orders

- `GET /orders/<tenant_id>`
- `POST /orders/`
- `PATCH /orders/<tenant_id>/<order_id>/cancel`
- `PATCH /orders/<tenant_id>/<order_id>/processing`
- `PATCH /orders/<tenant_id>/<order_id>/fulfill`
- `PATCH /orders/<tenant_id>/<order_id>/deliver`
- `POST /orders/<tenant_id>/<order_id>/refund`

### Wallet

- `GET /wallet/`
- `POST /wallet/credit`
- `POST /wallet/debit`
- `GET /wallet/tenants/<tenant_id>`

### Health

- `GET /health`

## Event-Driven Design

MartPlace uses a simple in-memory event bus to react to domain events after business actions complete.

Current event-driven integrations include:

- audit logging
- file-based event logging
- buyer order emails
- tenant-admin order emails
- user onboarding emails

This design makes it straightforward to add more listeners for features like notifications, analytics, or background processing.

## Logs and Generated Files

- event log: `logs/events.log`
- email log: `logs/emails.log`
- local SQLite database: `martplace.db`

## Testing

Run tests with:

```bash
pytest
```

Or:

```bash
python3 -m pytest
```

The repository already includes tests for:

- user registration and authentication
- tenant creation and management
- product creation and updates
- cart behavior
- wallet operations
- order lifecycle and refunds
- event bus handlers

## Limitations Today

- email delivery is file-based, not connected to a real provider
- the event bus is synchronous and in-memory
- notifications are email-only; there is no in-app notification center yet
- background jobs and message queue processing are not yet implemented
- observability is still lightweight

## TODO

### Product and Platform Improvements

- add persistent in-app notifications for tenant users
- add notification endpoints for listing, marking as read, and unread counts
- add a tenant activity feed for operational visibility
- add richer order filtering, search, and pagination
- add analytics dashboards for tenants and platform admins
- add inventory alerts such as low-stock warnings

### Infrastructure Improvements

- replace the file email service with a real email provider
- move from synchronous in-memory events to asynchronous event processing
- introduce a queue or broker for event delivery
- add retry and dead-letter handling for failed event processing
- improve structured logging and monitoring
- add error tracking and production-grade observability

### Security and Auth Improvements

- strengthen token/session management
- add password reset and email verification flows
- add finer-grained tenant permissions beyond current roles

### API and DX Improvements

- add OpenAPI/Swagger publishing guidance
- add seed scripts for demo data
- add containerization with Docker
- add CI for linting, tests, and migrations
- add deployment documentation

## Why MartPlace

MartPlace is a strong foundation for building marketplace systems because it already combines:

- multi-tenant boundaries
- transactional commerce flows
- role-aware access control
- extensible event-driven behavior
- clean separation between domain logic and infrastructure

It is a solid base for evolving from a local development backend into a more production-ready marketplace platform.
