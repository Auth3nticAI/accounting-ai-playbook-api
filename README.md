# Accounting AI Playbook — API

Backend for the Accounting AI Playbook: a library of accounting pain points and the AI solutions that address them. Built for solo founders running AI-for-accounting consultancies, so prospect conversations can land on real, priced, tech-stacked solutions instead of vague pitches.

CSE552 Mini Project 2 — full-stack CRUD with a one-to-many relationship.

## Stack

- **FastAPI** for the HTTP layer
- **SQLAlchemy** ORM
- **PostgreSQL 16** via Docker Compose
- **Pydantic** for request/response validation

## Domain model

Two tables with a one-to-many relationship:

```
pain_points (1) ──< (many) ai_solutions
```

- **`pain_points`** — a recurring accounting problem (title, description, category, firm_size_fit, severity)
- **`ai_solutions`** — an AI-backed approach to a pain point (title, description, tech_stack, maturity, setup_days, pricing_model, estimated_price_usd)

A single pain point can have multiple solutions (different maturity levels, different stacks, different pricing).

## Run

```bash
# 1. Start Postgres
docker compose up -d db

# 2. Activate venv and install
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Seed sample data (7 pain points + 9 solutions)
python seed.py

# 4. Start the API
uvicorn main:app --reload
```

Open http://localhost:8000/docs for the Swagger UI.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/stats` | Aggregate counts (by category, severity, maturity) |
| GET | `/categories` | List of distinct pain-point categories |
| GET | `/pain-points` | List all pain points (filter by `?category=` or `?severity=`) |
| POST | `/pain-points` | Create a new pain point |
| GET | `/pain-points/{id}` | Pain point detail with all its solutions |
| PUT | `/pain-points/{id}` | Update a pain point (partial) |
| DELETE | `/pain-points/{id}` | Delete a pain point (cascades to solutions) |
| POST | `/pain-points/{id}/solutions` | Add a new solution to a pain point |
| PUT | `/solutions/{id}` | Update a solution (partial) |
| DELETE | `/solutions/{id}` | Delete a solution |

## Environment

Create `.env` (gitignored):

```
DATABASE_URL=postgresql://postgres:password@localhost:5432/playbook
```

## Layout

```
.
├── main.py            # FastAPI app + route handlers + CORS
├── database.py        # Engine, SessionLocal, Base, get_db dependency
├── models.py          # SQLAlchemy ORM models (PainPoint, AISolution)
├── schemas.py         # Pydantic request/response schemas
├── seed.py            # Idempotent seed script
├── docker-compose.yml # Postgres service
└── requirements.txt
```
