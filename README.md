# MartPlace

MartPlace is a multi-tenant marketplace backend built for buyers, tenant vendors, and platform administrators. It provides authentication, tenant onboarding, product and inventory management, cart and checkout flows, wallet-based transactions, a full order lifecycle, and event-driven logging and notifications.

## Highlights

- Multi-tenant commerce architecture
- Role-based access control (Buyer, Tenant Admin, Tenant Staff, Platform Admin)
- Product catalog & stock management
- Multi-item shopping cart & atomic checkout
- Wallet credit/debit flows for buyers & automatic tenant wallet crediting on sales
- Complete order lifecycle handling:
  - `create`
  - `processing`
  - `fulfilled`
  - `delivered`
  - `cancelled`
  - `refunded`
- Event-driven audit logging and email notification pipeline
- Containerized development & production deployment via Docker and Docker Compose

---

## Tech Stack

- **Language:** Python 3.11+
- **Web Framework:** Quart (Async ASGI framework) with `quart-schema` (OpenAPI/Swagger docs) & `quart-cors`
- **Database & ORM:** SQLAlchemy 2.x (async), SQLite (`aiosqlite`) for local dev, PostgreSQL-ready (`asyncpg`)
- **Migrations:** Alembic
- **Containerization:** Docker (Multi-stage build) & Docker Compose
- **Testing:** Pytest & Pytest-Asyncio

---

## Core Domain

MartPlace models a marketplace where:

- **Buyers** register, authenticate, manage wallets, browse marketplace products, manage cart items, place orders, and receive order status updates.
- **Tenant Admins** create and manage tenant products, oversee tenant orders through their lifecycle, and monitor tenant wallet balances.
- **Tenant Staff** operate within a tenant's workspace under role restrictions.
- **Platform Admins** oversee tenants across the platform (activating, suspending, and monitoring platform activity).

---

## Project Structure

```text
MartPlace/
├── app/
│   ├── domain/            # Entities, domain events, value objects, domain exceptions
│   ├── interfaces/        # Contracts for repositories, email services, event bus
│   ├── use_cases/         # Application business logic & orchestrations
│   ├── infrastructure/
│   │   ├── db/            # SQLAlchemy models, repositories, mappers, DB configuration
│   │   ├── event_handlers/# Event listeners (audit, event logging, email dispatchers)
│   │   ├── services/      # Service implementations (file-backed email service)
│   │   └── web/           # Quart app, routes, auth, schemas, error handlers
│   ├── bootstrap.py       # Application runtime initialization
│   └── platform_admin.py  # Platform admin setup logic
├── migrations/            # Alembic database migration scripts
├── tests/                 # Unit and integration test suite
├── Dockerfile             # Multi-stage Docker build file
├── docker-compose.yaml    # Docker Compose service definition
├── .dockerignore          # Docker build exclusion rules
├── .env.example           # Environment variables template
├── alembic.ini            # Alembic configuration file
├── main.py                # Application entrypoint & CLI manager
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
```

---

## Environment Configuration

Copy `.env.example` to create your local `.env` configuration:

```bash
cp .env.example .env
```

### Supported Environment Variables

| Variable | Default | Description |
| :--- | :--- | :--- |
| `QUART_ENV` | `development` | Runtime environment (`development`, `production`) |
| `QUART_DEBUG` | `true` | Enable or disable Quart debug mode |
| `HOST` | `0.0.0.0` | Server bind host address |
| `PORT` | `50055` | Server bind port |
| `DATABASE_URL` | `sqlite+aiosqlite:///martplace.db` | Async database connection string |
| `SQLALCHEMY_ECHO` | `false` | Enable SQL query echo logging |
| `SECRET_KEY` | `change-me` | Secret key used for JWT signing and session security |
| `AUTH_TOKEN_MAX_AGE` | `900` | Access token expiration in seconds (15 minutes) |
| `AUTH_REFRESH_TOKEN_MAX_AGE` | `604800` | Refresh token expiration in seconds (7 days) |
| `EVENT_LOG_PATH` | `logs/events.log` | File path for appended domain event logs |
| `EMAIL_LOG_PATH` | `logs/emails.log` | File path for emitted email notifications |

---

## Docker Setup & Deployment

MartPlace provides containerization using a multi-stage Docker build (`python:3.11-slim`) and Docker Compose.

### Features of the Docker Setup

- **Multi-stage build:** Separates build dependencies (`build-essential`, `libpq-dev`) from the lean runtime image (`libpq5`, `curl`).
- **Security hardening:** Runs under a non-root system user (`appuser`).
- **Automated migrations:** Runs `alembic upgrade head` automatically prior to launching the server.
- **Built-in health checking:** Periodically checks `http://localhost:50055/health`.
- **Persistent storage:** Mounts local host paths for `martplace.db` and `logs/` to preserve database states and log files across container restarts.

### 1. Running with Docker Compose (Recommended)

Start the containerized service in detached mode:

```bash
docker compose up -d
```

Check running status and health:

```bash
docker compose ps
```

View container logs:

```bash
docker compose logs -f
```

Stop the service:

```bash
docker compose down
```

### 2. Running directly with Docker CLI

Build the image:

```bash
docker build -t teejay/martplace .
```

Run the container with volume mounts:

```bash
docker run -d \
  --name martplace \
  -p 50055:50055 \
  -v $(pwd)/martplace.db:/martplace/martplace.db \
  -v $(pwd)/logs:/martplace/logs \
  teejay/martplace
```

---

## Local Development (Without Docker)

### 1. Prerequisites

- Python 3.11+
- `pip` and `virtualenv`

### 2. Setup Virtual Environment

```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
pip install pytest
```

### 3. Run Database Migrations

Apply database schema migrations using Alembic:

```bash
alembic upgrade head
```

### 4. Run the Server

Launch the API server using `main.py`:

```bash
python3 main.py serve --debug
```

or simply:

```bash
python3 main.py
```

The application will be accessible at `http://localhost:50055`.

---

## CLI & Management Commands

`main.py` serves as the CLI manager for running the app and executing utility tasks:

### Start API Server (`serve`)

```bash
python3 main.py serve [--host HOST] [--port PORT] [--debug]
```

- `--host`: Bind address (default: `0.0.0.0` or `$HOST`)
- `--port`: Listen port (default: `50055` or `$PORT`)
- `--debug`: Run Quart server in debug mode

### Test Event Emission (`emit-test-event`)

Test the event bus dispatcher and log writers without running the HTTP server:

```bash
python3 main.py emit-test-event --email "buyer@example.com" --name "Test Buyer"
```

This publishes a `BuyerRegistered` event to test that domain events are properly handled and logged to `logs/events.log` and `logs/emails.log`.

---

## API Overview & Endpoints

Interactive OpenAPI documentation is available via Quart Schema when running the server:
- **Swagger UI:** `http://localhost:50055/docs`
- **OpenAPI Schema:** `http://localhost:50055/openapi.json`

### Key Endpoints

#### System & Health
- `GET /health` - Service health status check

#### Authentication (`/auth`)
- `POST /auth/login` - Authenticate user & obtain access/refresh tokens
- `POST /auth/refresh` - Refresh access token
- `POST /auth/logout` - Invalidate current session

#### User Management (`/users`)
- `POST /users/buyers` - Register buyer account
- `POST /users/tenant-users` - Register tenant user account
- `GET /users/` - List users
- `GET /users/<user_id>` - Get user details

#### Tenant Management (`/tenants`)
- `POST /tenants/` - Create tenant (optionally creates initial tenant admin)
- `GET /tenants/` - List tenants
- `GET /tenants/active` - List active tenants
- `GET /tenants/<tenant_id>` - Get tenant details
- `PATCH /tenants/<tenant_id>/activate` - Activate tenant
- `PATCH /tenants/<tenant_id>/suspend` - Suspend tenant

#### Product Catalog (`/products`)
- `POST /products/` - Create product under tenant
- `GET /products/` - List all marketplace products
- `GET /products/<tenant_id>` - List products for specific tenant
- `GET /products/<tenant_id>/<product_id>` - Get specific product details
- `PATCH /products/<tenant_id>/<product_id>/update` - Update product price/stock

#### Cart & Checkout (`/cart`)
- `GET /cart/` - View current buyer's cart
- `POST /cart/items` - Add item to cart
- `DELETE /cart/items` - Remove item from cart
- `POST /cart/checkout` - Checkout cart items into tenant orders

#### Order Lifecycle (`/orders`)
- `POST /orders/` - Create order directly
- `GET /orders/<tenant_id>` - List orders for a tenant
- `PATCH /orders/<tenant_id>/<order_id>/processing` - Transition order to processing
- `PATCH /orders/<tenant_id>/<order_id>/fulfill` - Mark order fulfilled
- `PATCH /orders/<tenant_id>/<order_id>/deliver` - Mark order delivered
- `PATCH /orders/<tenant_id>/<order_id>/cancel` - Cancel order
- `POST /orders/<tenant_id>/<order_id>/refund` - Issue order refund

#### Wallet Operations (`/wallet`)
- `GET /wallet/` - Get buyer wallet details
- `POST /wallet/credit` - Credit buyer wallet balance
- `POST /wallet/debit` - Debit buyer wallet balance
- `GET /wallet/tenants/<tenant_id>` - Get tenant wallet balance

---

## Event-Driven Architecture & Logging

MartPlace utilizes an asynchronous, in-memory event bus powered by a background `ThreadPoolExecutor` (via Blinker signals) to process domain events non-blockingly after business operations complete:

1. **Domain Events:** `BuyerRegistered`, `OrderCreated`, `OrderFulfilled`, `OrderDelivered`, `OrderCancelled`, `OrderRefunded`, etc.
2. **Asynchronous Execution:** Event handlers run in background worker threads without blocking request execution times.
3. **Audit Logging:** Domain events are formatted and appended asynchronously to `logs/events.log`.
4. **Email Dispatcher:** Triggered event listeners construct notifications asynchronously recorded in `logs/emails.log`.

---

## Testing

Execute the test suite using `pytest`:

```bash
pytest
```

or:

```bash
python3 -m pytest
```

---

## Future Roadmap

- [ ] Connect file email service to SMTP / external provider (SendGrid, SES)
- [ ] Transition from in-memory `ThreadPoolExecutor` events to a distributed message queue / broker (RabbitMQ / Redis / Celery) for multi-process scalability
- [ ] Add persistent in-app notifications & activity feed for tenant users
- [ ] Add advanced search, filtering, and pagination across order & product endpoints
- [ ] Add analytics dashboard endpoints for platform and tenant metrics


