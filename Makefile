.PHONY: dev prod test test-be test-fe coverage lint lint-fix install-be install-fe run-be run-fe clean logs help

# ─── Colors ─────────────────────────────────────────────────────────────────
CYAN  := \033[0;36m
GREEN := \033[0;32m
RESET := \033[0m

# ─── Docker ──────────────────────────────────────────────────────────────────

## Start development environment
dev:
	@echo "$(CYAN)🚀 Starting FlowBoard dev environment...$(RESET)"
	docker compose up --build

## Start production environment
prod:
	@echo "$(CYAN)🚀 Starting FlowBoard production environment...$(RESET)"
	docker compose -f docker-compose.prod.yml up --build

## Stop all containers and remove volumes
clean:
	@echo "$(CYAN)🧹 Cleaning up containers...$(RESET)"
	docker compose down -v --remove-orphans
	docker compose -f docker-compose.prod.yml down -v --remove-orphans 2>/dev/null || true

## Tail container logs
logs:
	docker compose logs -f

# ─── Testing ─────────────────────────────────────────────────────────────────

## Run all tests
test: test-be test-fe

## Run backend tests
test-be:
	@echo "$(CYAN)🧪 Running backend tests...$(RESET)"
	cd backend && python -m pytest tests/ -v

## Run frontend tests
test-fe:
	@echo "$(CYAN)🧪 Running frontend tests...$(RESET)"
	cd frontend && npm run test

## Run all tests with coverage
coverage:
	@echo "$(CYAN)📊 Running tests with coverage...$(RESET)"
	cd backend && python -m pytest tests/ -v --cov=app --cov-report=term-missing --cov-fail-under=80
	cd frontend && npm run test:coverage

# ─── Linting ─────────────────────────────────────────────────────────────────

## Lint all code
lint: lint-be lint-fe

## Lint backend
lint-be:
	@echo "$(CYAN)🔍 Linting backend...$(RESET)"
	cd backend && ruff check app/ tests/
	cd backend && black --check app/ tests/

## Lint frontend
lint-fe:
	@echo "$(CYAN)🔍 Linting frontend...$(RESET)"
	cd frontend && npm run lint
	cd frontend && npm run format:check

## Auto-fix lint issues
lint-fix:
	@echo "$(GREEN)✨ Auto-fixing lint issues...$(RESET)"
	cd backend && ruff check --fix app/ tests/
	cd backend && black app/ tests/
	cd frontend && npm run lint:fix
	cd frontend && npm run format

# ─── Local Dev (no Docker) ───────────────────────────────────────────────────

## Install backend dependencies
install-be:
	@echo "$(CYAN)📦 Installing backend dependencies...$(RESET)"
	cd backend && pip install -r requirements.txt

## Install frontend dependencies
install-fe:
	@echo "$(CYAN)📦 Installing frontend dependencies...$(RESET)"
	cd frontend && npm install

## Run backend locally
run-be:
	@echo "$(CYAN)🐍 Starting FastAPI backend on :8000...$(RESET)"
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

## Run frontend locally
run-fe:
	@echo "$(CYAN)⚛️  Starting Vite frontend on :5173...$(RESET)"
	cd frontend && npm run dev

# ─── Help ────────────────────────────────────────────────────────────────────

## Show this help
help:
	@echo "$(CYAN)FlowBoard — Available Commands$(RESET)"
	@echo "================================"
	@grep -E '^##' Makefile | sed 's/## /  /'
