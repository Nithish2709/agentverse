# PDS Sentinel AI — Stage 1 Foundation

> Agentic AI platform for monitoring India's Public Distribution System (PDS).
> This repository contains the **Stage 1 backend foundation** — a production-ready FastAPI service with PostgreSQL, Redis, JWT auth, and RBAC.

---

## Tech Stack

| Layer | Technology |
|---|---|
| API | FastAPI 0.115, Python 3.12 |
| ORM | SQLAlchemy 2.x (async) |
| Migrations | Alembic |
| Database | PostgreSQL 16 |
| Cache | Redis 7 |
| Auth | JWT (python-jose) + bcrypt |
| Config | Pydantic Settings |
| Logging | structlog (JSON) |
| Testing | Pytest + pytest-asyncio |
| Linting | Ruff + Black |
| Deployment | Docker + Docker Compose |

---

## Quick Start (Local)

### Prerequisites
- Python 3.12+
- PostgreSQL 16
- Redis 7
- [uv](https://github.com/astral-sh/uv) or pip

### 1. Clone and configure

```bash
cd backend
cp .env.example .env
# Edit .env — set SECRET_KEY, DATABASE_URL, REDIS_URL
```

### 2. Create virtual environment and install dependencies

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -e ".[dev]"
```

### 3. Initialize PostgreSQL

```bash
# Create database and user
psql -U postgres -c "CREATE USER pds_user WITH PASSWORD 'pds_password';"
psql -U postgres -c "CREATE DATABASE pds_sentinel OWNER pds_user;"
psql -U postgres -d pds_sentinel -f ../scripts/init_db.sql
```

### 4. Run Alembic migrations

```bash
cd backend
alembic upgrade head
```

### 5. Start the server

```bash
uvicorn asgi:app --reload --host 0.0.0.0 --port 8000
```

API docs: http://localhost:8000/docs

---

## Docker

### Start all services

```bash
docker compose up --build
```

### Start with Adminer (DB UI)

```bash
docker compose --profile tools up --build
```

### Run migrations inside container

```bash
docker compose exec api alembic upgrade head
```

### Seed default admin user

```bash
docker compose exec api bash scripts/seed_admin.sh
```

---

## Alembic Migration Commands

```bash
# Apply all pending migrations
alembic upgrade head

# Create a new migration (auto-detect model changes)
alembic revision --autogenerate -m "describe your change"

# Downgrade one step
alembic downgrade -1

# Show current revision
alembic current

# Show migration history
alembic history --verbose
```

---

## Testing

```bash
# Run all tests with coverage
pytest

# Run only unit tests
pytest app/tests/unit/

# Run only integration tests
pytest app/tests/integration/

# Run with verbose output, no coverage
pytest -v --no-cov
```

---

## Linting & Formatting

```bash
# Lint with Ruff
ruff check .

# Auto-fix lint issues
ruff check . --fix

# Format with Black
black .

# Check formatting without writing
black . --check

# Type check with mypy
mypy app/

# Run all pre-commit hooks
pre-commit run --all-files

# Install pre-commit hooks
pre-commit install
```

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/ping` | Liveness probe |
| GET | `/api/v1/health` | Readiness probe (DB + Redis) |
| POST | `/api/v1/auth/login` | Obtain JWT token pair |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| POST | `/api/v1/users` | Create user (USER_WRITE) |
| GET | `/api/v1/users` | List users (USER_READ) |
| GET | `/api/v1/users/me` | Current user profile |
| GET | `/api/v1/users/{id}` | Get user by ID (USER_READ) |
| PATCH | `/api/v1/users/{id}` | Update user (USER_WRITE) |

---

## RBAC Roles

| Role | Key Permissions |
|---|---|
| `super_admin` | All permissions |
| `admin` | User + Report + Agent management |
| `analyst` | Read users, read/write reports, read agents |
| `field_officer` | Read/write reports |
| `viewer` | Read reports and users |

---

## Project Structure

```
pds-sentinel-ai/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # Versioned route handlers
│   │   ├── config/          # Pydantic Settings
│   │   ├── core/            # Security, logging, exceptions
│   │   ├── database/        # SQLAlchemy engine + Redis pool
│   │   ├── middleware/       # Exception handler, logging, rate limit
│   │   ├── models/          # SQLAlchemy ORM models
│   │   ├── repositories/    # Data access layer
│   │   ├── schemas/         # Pydantic request/response schemas
│   │   ├── services/        # Business logic layer
│   │   ├── agents/          # Placeholder — Stage 2 LangGraph agents
│   │   ├── graph/           # Placeholder — Stage 2 LangGraph graph
│   │   ├── utils/           # Shared utilities
│   │   └── tests/           # Unit + integration tests
│   ├── alembic/             # Database migrations
│   ├── scripts/             # DB init and seed scripts
│   ├── asgi.py              # ASGI entry point
│   ├── pyproject.toml       # Dependencies + tool config
│   ├── Dockerfile
│   └── .env.example
├── scripts/
│   └── init_db.sql
├── docker-compose.yml
└── .gitignore
```

---

## Verification Checklist

- [ ] `GET /api/v1/ping` returns `{"ping": "pong"}`
- [ ] `GET /api/v1/health` returns `{"status": "healthy", ...}`
- [ ] `POST /api/v1/auth/login` returns JWT token pair
- [ ] `GET /api/v1/users/me` returns 401 without token
- [ ] `alembic upgrade head` creates `users` table
- [ ] `pytest` passes with ≥70% coverage
- [ ] `ruff check .` reports no errors
- [ ] `black . --check` reports no formatting issues
- [ ] Docker Compose starts all three services healthy
- [ ] Logs output structured JSON in production mode
