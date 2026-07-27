# Architecture — PDS Sentinel AI

## Overview

PDS Sentinel AI is a multi-agent platform built on **Clean Architecture** principles. The backend is organized into concentric layers where dependencies always point inward.

```
┌─────────────────────────────────────────────────────┐
│                   API Layer (FastAPI)                │
│         Routers → Endpoints → Dependencies          │
├─────────────────────────────────────────────────────┤
│                  Service Layer                       │
│           Business logic, orchestration             │
├─────────────────────────────────────────────────────┤
│               Repository Layer                       │
│         Data access, query abstraction              │
├─────────────────────────────────────────────────────┤
│                  Domain Layer                        │
│        Models, Schemas, Exceptions, RBAC            │
├─────────────────────────────────────────────────────┤
│              Infrastructure Layer                    │
│       PostgreSQL, Redis, Alembic, Logging           │
└─────────────────────────────────────────────────────┘
```

---

## Module Responsibilities

| Module | Responsibility |
|---|---|
| `app/config/` | Pydantic Settings — single source of truth for all env vars |
| `app/core/` | Security (JWT, RBAC), hashing, logging, exception hierarchy |
| `app/database/` | SQLAlchemy async engine, session factory, Redis pool |
| `app/models/` | SQLAlchemy ORM models with shared mixins |
| `app/schemas/` | Pydantic request/response contracts |
| `app/repositories/` | Generic + model-specific data access (Repository Pattern) |
| `app/services/` | Business logic, coordinates repositories |
| `app/api/` | FastAPI routers, dependency injection wiring |
| `app/middleware/` | Cross-cutting concerns: logging, rate limiting, error handling |
| `app/agents/` | Placeholder — LangGraph agent implementations (Stage 2) |
| `app/graph/` | Placeholder — LangGraph StateGraph orchestration (Stage 2) |
| `app/utils/` | Shared stateless helpers |

---

## Request Lifecycle

```
HTTP Request
    │
    ▼
CORSMiddleware
    │
    ▼
RequestLoggingMiddleware  ← attaches request_id, logs latency
    │
    ▼
RateLimitMiddleware       ← Redis sliding window counter
    │
    ▼
ExceptionHandlerMiddleware ← maps AppError → JSON response
    │
    ▼
FastAPI Router
    │
    ▼
Dependency Injection      ← DB session, Redis, token validation
    │
    ▼
Endpoint Handler
    │
    ▼
Service Layer             ← business logic
    │
    ▼
Repository Layer          ← SQL queries via SQLAlchemy
    │
    ▼
PostgreSQL / Redis
```

---

## Authentication Flow

```
POST /auth/login
    │
    ▼
UserService.authenticate()
    │  verifies bcrypt hash
    ▼
create_token_pair()
    │  access_token (30 min HS256 JWT)
    │  refresh_token (7 day HS256 JWT)
    ▼
TokenResponse → client

Subsequent requests:
Authorization: Bearer <access_token>
    │
    ▼
get_current_token() dependency
    │  decode_token() → TokenPayload
    ▼
require_permission() guard
    │  checks payload.permissions
    ▼
Endpoint handler
```

---

## RBAC Model

Permissions are embedded in the JWT at issuance time. No database lookup is needed per request.

```
Role ──► set[Permission]
         │
         └─ encoded in JWT payload
                │
                └─ validated by require_permission() dependency
```

---

## Stage 2 Extension Points

The following placeholders are ready for Stage 2:

- `app/agents/` — one file per LangGraph agent
- `app/graph/` — StateGraph definition and node wiring
- `app/services/` — agent orchestration service
- `app/api/v1/endpoints/` — agent trigger and status endpoints
- `docker-compose.yml` — Celery worker service (add under `services:`)
