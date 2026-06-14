# Accounting AI Playbook — API

![CI](https://github.com/Auth3nticAI/accounting-ai-playbook-api/actions/workflows/ci.yml/badge.svg)

> Backend for [Accounting AI Playbook](https://github.com/Auth3nticAI/accounting-ai-playbook). A catalog of recurring accounting pain points (close cycle, AP coding, audit prep) mapped to AI solutions you can actually offer — each with stack, maturity level, setup days, and a target price.
>
> Built so a solo AI-for-accounting consultant can show up to a prospect call with priced, tech-stacked answers instead of vapor.

![FastAPI](https://img.shields.io/badge/FastAPI-0.136-009688?style=flat&logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=flat)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=flat&logo=postgresql&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-2.13-E92063?style=flat&logo=pydantic&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat&logo=docker&logoColor=white)

---


![header](screenshots/header.png)

## Domain model

One-to-many: a pain point can have multiple AI solutions (different maturity levels, different stacks, different price points).

```
pain_points (1) ──< (many) ai_solutions
```

- **`pain_points`** — `title`, `description`, `category`, `firm_size_fit`, `severity`
- **`ai_solutions`** — `title`, `description`, `tech_stack`, `maturity`, `setup_days`, `pricing_model`, `estimated_price_usd`

`ON DELETE CASCADE` on the FK so removing a pain point cleans up its mapped solutions.

## Endpoints

| Method | Path | What it does |
|---|---|---|
| `GET` | `/health` | Health check |
| `GET` | `/stats` | Aggregate counts (by category, severity, maturity) — drives the frontend home page |
| `GET` | `/categories` | Distinct pain-point categories |
| `GET` | `/pain-points` | List + filter by `?category=` and `?severity=` |
| `POST` | `/pain-points` | Create |
| `GET` | `/pain-points/{id}` | Detail + all mapped solutions |
| `PUT` | `/pain-points/{id}` | Partial update |
| `DELETE` | `/pain-points/{id}` | Delete (cascades) |
| `POST` | `/pain-points/{id}/solutions` | Add a solution to a pain point |
| `PUT` | `/solutions/{id}` | Partial update |
| `DELETE` | `/solutions/{id}` | Delete a single solution |

## Run

```bash
docker compose up -d db
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Seed 7 pain points + 9 solutions
python seed.py

# Start the API
uvicorn main:app --reload
```

Swagger UI: http://localhost:8000/docs

## Env

```
DATABASE_URL=postgresql://postgres:password@localhost:5432/playbook
```

## Layout

```
.
├── main.py             # FastAPI routes
├── database.py         # Engine, SessionLocal, Base, get_db
├── models.py           # SQLAlchemy ORM
├── schemas.py          # Pydantic
├── seed.py             # Idempotent realistic seed data
├── docker-compose.yml  # Postgres service
└── requirements.txt
```

## Background

Built as Mini Project 2 for **CSE552 — Fullstack Software Development in the Age of AI Agents**.
