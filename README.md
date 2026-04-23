# FlowBoard 🚀

> A production-grade Task Management SaaS — built for the **DevOps Workshop: A Day in the Life of a Developer**

[![CI](https://github.com/your-org/not_jenkins/actions/workflows/ci.yml/badge.svg)](https://github.com/your-org/not_jenkins/actions)
[![CD Staging](https://github.com/your-org/not_jenkins/actions/workflows/cd-staging.yml/badge.svg)](https://github.com/your-org/not_jenkins/actions)

---

## 📚 Workshop Overview

This project demonstrates a complete, production-grade DevOps lifecycle:

| Step | What We Cover |
|------|--------------|
| 🌿 Git Branching | `main` → `dev` → `feature/*` strategy |
| 🔁 Pull Requests | Feature → dev → main with CI gates |
| 🧪 Automated Testing | Pytest (backend) + Vitest (frontend) |
| 🔍 Linting | Ruff + Black (BE) · ESLint + Prettier (FE) |
| 🐳 Docker | Multi-stage builds, dev + prod compose |
| ⚙️ CI/CD | GitHub Actions: lint → test → build → deploy |

---

## 🏗️ Tech Stack

**Backend:** FastAPI · Python 3.12 · JWT Auth · In-memory store (DB-ready)  
**Frontend:** React 18 · Vite · TypeScript · Dark glassmorphism UI  
**DevOps:** Docker · Docker Compose · GitHub Actions · GHCR  

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node 20+ (for local frontend dev)
- Python 3.12+ (for local backend dev)

### Run with Docker (recommended)

```bash
# Copy environment config
cp .env.example .env

# Start all services
make dev

# App runs at:
#   Frontend → http://localhost:5173
#   Backend API → http://localhost:8000
#   API Docs → http://localhost:8000/docs
```

### Run locally (without Docker)

```bash
# Backend
make install-be
make run-be

# Frontend (new terminal)
make install-fe
make run-fe
```

---

## 🧪 Testing

```bash
# Run all tests
make test

# Backend only
make test-be

# Frontend only
make test-fe

# With coverage report
make coverage
```

---

## 🔍 Linting

```bash
# Lint everything
make lint

# Auto-fix
make lint-fix
```

---

## 🌿 Branching Strategy

```
main ──────────────────────────── Production (protected)
  └── dev ─────────────────────── Staging (protected)
        ├── feature/auth ─────── Backend auth + API
        └── feature/ui ───────── Frontend React app
```

**Branch protection rules:**
- `main`: Requires PR + all CI checks passing
- `dev`: Requires PR + all CI checks passing

**Commit convention:** [Conventional Commits](https://www.conventionalcommits.org/)
```
feat(auth): add JWT refresh endpoint
fix(tasks): resolve status filter edge case
test(boards): add concurrent update tests
ci: parallelize lint and test jobs
```

---

## 🐳 Docker Architecture

### Development
```
docker-compose.yml
├── backend   (uvicorn --reload, port 8000)
└── frontend  (vite dev server, port 5173)
```

### Production
```
docker-compose.prod.yml
├── nginx     (reverse proxy, ports 80/443)
├── backend   (multi-stage slim build)
└── frontend  (nginx:alpine static serve)
```

---

## ⚙️ GitHub Actions Workflows

| Workflow | Trigger | Jobs |
|---------|---------|------|
| `ci.yml` | PR → `main`/`dev` | lint-be · lint-fe · test-be · test-fe · docker-build |
| `cd-staging.yml` | Push → `dev` | test → build+push → deploy-staging |
| `cd-production.yml` | Push → `main` | test → build+push → deploy-production |

---

## 📁 Project Structure

```
not_jenkins/
├── .github/workflows/   # CI/CD pipeline definitions
├── backend/             # FastAPI application
│   ├── app/             # Application code
│   └── tests/           # Pytest test suite
├── frontend/            # React + Vite application
│   └── src/             # Application source
├── docker-compose.yml   # Development environment
├── docker-compose.prod.yml  # Production environment
└── Makefile             # Developer convenience commands
```

---

## 🛠️ Makefile Commands

```bash
make dev          # Start dev environment (Docker)
make prod         # Start prod environment (Docker)
make test         # Run all tests
make test-be      # Backend tests only
make test-fe      # Frontend tests only
make coverage     # Tests with coverage report
make lint         # Lint all code
make lint-fix     # Auto-fix linting issues
make install-be   # Install backend dependencies
make install-fe   # Install frontend dependencies
make run-be       # Run backend (local)
make run-fe       # Run frontend (local)
make clean        # Stop and remove containers
make logs         # Tail container logs
```

---

## 📝 License

MIT — built for education purposes as part of the DevOps Workshop series.
