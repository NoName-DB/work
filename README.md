# Business Template (Python SaaS Starter)

A modular Python starter project designed for fast customization and delivery to businesses.

## ✅ What you get

- **FastAPI API skeleton** for building backend services
- **Auth-ready** (JWT + password hashing) user management
- **SQLAlchemy** + database session support (SQLite / Postgres)
- **Modular architecture** for easy feature expansion
- **Docker + Compose** for local development and deployment

## 🚀 Getting started

### 1) Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2) Install dependencies

Option A (quick):

```bash
pip install -r requirements.txt
```

Option B (recommended for development):

```bash
pip install -e .
```

### 3) Run the API

```bash
uvicorn business_template.main:app --reload
```

Then open http://localhost:8000/docs for the auto-generated Swagger UI.

## 🧩 Customizing for your business

This template is intentionally opinionated but minimal. Add new feature modules under `src/business_template/`:

- `api/` — define new routes and routers
- `crud/` — business logic for database actions
- `models/` — database models
- `schemas/` — request/response models

## 📦 Deployment

Build and run with Docker:

```bash
docker compose up --build
```

---

## 🎯 Next steps (examples)

- Add multi-tenant support
- Add role-based access control (RBAC)
- Add billing / subscription module
- Add logging / monitoring hooks
