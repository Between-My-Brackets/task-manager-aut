# FlowBoard 🚀 — Detailed Architecture & Project Documentation

FlowBoard is a production-grade Task Management SaaS application created as the capstone project for the **DevOps Workshop: A Day in the Life of a Developer**.

This README contains the comprehensive, deep-dive architecture and technical documentation for the codebase.  
> **⚠️ Presenting the workshop?** Please see [WORKSHOP_GUIDE.md](./WORKSHOP_GUIDE.md) for your step-by-step, spoon-fed script.

---

## 🏗️ System Architecture

FlowBoard employs a modern, decoupled client-server architecture:

```text
[ Client Request ]
       |
       v
[ Reverse Proxy (Nginx) ]  ---> Serves static React/Vite Frontend
       |
       v
[ FastAPI API Backend ]  ---> Handles stateless JWT authentication
       |
       v
[ In-Memory Store ]  ---> (Abstracted Data Layer — swappable to PostgreSQL)
```

### 1. The Backend (FastAPI + Python 3.12)
The backend is a blazing-fast Python API built on standard asynchronous paradigms.
*   **Framework:** FastAPI with Uvicorn server.
*   **Authentication:** Stateless JWT (JSON Web Tokens). Passwords are cryptographically hashed using `bcrypt` via standard `passlib`.
*   **Data Validation:** Handled by Pydantic V2 strictly validating incoming JSON payloads against schemas.
*   **Data Persistence:** To allow for a completely zero-friction developer setup, the backend utilizes a Thread-Safe In-Memory Singleton Store (`app/store.py`). Data is stored in dictionaries protected by `threading.Lock`. Because the data layer is decoupled, it can be seamlessly swapped out for SQLAlchemy/Postgres by rewriting the store class methods without touching a single API route.
*   **Testing:** Comprehensive `pytest` test suite with dependency injection. The store teardown is automated between every single test to ensure 100% isolation. Test coverage is enforced to be above 80%.

### 2. The Frontend (React 18 + Vite + TypeScript)
The UI is a highly interactive, Single Page Application (SPA).
*   **Framework:** React 18 initialized via Vite for instantaneous Hot Module Replacement (HMR).
*   **Language:** Strict TypeScript ensuring type safety across API calls.
*   **Design System:** A custom, dependency-free CSS design system located in `index.css`. It features modern "Dark Glassmorphism", CSS custom variables for theming, animated statistics counters, and responsive flex/grid layouts.
*   **State Management & API:** React Hooks paired with `axios`. An Axios HTTP interceptor automatically grabs the JWT from `localStorage` and injects it into the `Authorization: Bearer <token>` header for all outbound requests.
*   **Testing:** `vitest` combined with React Testing Library (`@testing-library/react`) mocks DOM rendering and user events (clicks, typing).

### 3. Containerization (Docker)
Both the backend and frontend employ **Multi-Stage Dockerfiles** to achieve minimal image sizes and enhanced security.
*   **Backend Dockerfile:** The "Builder" stage downloads compile-heavy libraries (like `bcrypt`) via `gcc`. The "Runtime" stage uses a bare-minimum `python:3.12-slim` image, copies only the compiled binaries, and runs as a non-root `appuser`.
*   **Frontend Dockerfile:** The "Node Builder" stage compiles the React/TypeScript code into static HTML/JS/CSS assets. The "Runtime" stage completely discards Node.js, spinning up purely `nginx:alpine` to serve the static assets alongside advanced GZip and cache-control configurations.

---

## 📚 API Endpoints

The backend completely auto-documents itself via OpenAPI. When running locally, visit `http://localhost:8000/docs`.

### Authentication
*   `POST /auth/register`: Create a new user account.
*   `POST /auth/login`: Exchange username/password for a JWT access token.
*   `GET /auth/me`: Retrieve the currently authenticated user's profile.

### Boards
*   `GET /boards`: List all boards belonging to the logged-in user.
*   `POST /boards`: Create a new Kanban board.
*   `GET /boards/{board_id}`: Retrieve metadata for a specific board.
*   `DELETE /boards/{board_id}`: Delete a board and automatically cascade-delete all its tasks.

### Tasks
*   `GET /boards/{board_id}/tasks`: List all tasks (supports query filtering like `?status=todo&priority=high`).
*   `POST /boards/{board_id}/tasks`: Add a task to a board.
*   `PUT /boards/{board_id}/tasks/{task_id}`: Partially update a task's status, title, or priority.
*   `DELETE /boards/{board_id}/tasks/{task_id}`: Delete a specific task.

### Analytics
*   `GET /dashboard/stats`: Returns aggregated counts for boards, completed tasks etc., powering the UI's animated widgets.

---

## 📁 Repository Map

```text
not_jenkins/
├── .github/workflows/          # Definitions for GitHub Actions CI/CD
│   ├── ci.yml                  # PR gating: Lint, Test, Coverage, Build Testing
│   ├── cd-staging.yml          # On dev push: Build real image & fake deploy
│   └── cd-production.yml       # On main push: Versioned images & zero-downtime fake deploy
├── backend/                    
│   ├── app/                    # FastAPI application root
│   │   ├── routers/            # Endpoint handlers (controllers)
│   │   ├── auth/               # JWT & Password hashing utilities
│   │   ├── schemas.py          # API request/response definitions
│   │   └── store.py            # In-memory database logic
│   ├── tests/                  # Pytest test files
│   └── Dockerfile              # Multi-stage python image
├── frontend/                   
│   ├── src/                    
│   │   ├── pages/              # React Page components (Dashboard, Boards)
│   │   ├── services/           # Axios API connectors
│   │   └── __tests__/          # Vitest testing suite
│   ├── Dockerfile              # Node build -> Nginx runtime image
│   └── nginx.conf              # Nginx rules for Single Page App routing
├── docker-compose.yml          # Local development wrapper (Hot Reloading)
├── docker-compose.prod.yml     # Production architecture wrapper
└── Makefile                    # Local convenience commands (make dev, make test)
```

---

## 🚀 Running Locally

There are two ways to run FlowBoard locally: using Docker (recommended) or running the frontend and backend separately.

### Option 1: Docker (Recommended)
You can bring up both the frontend and backend with hot-reloading using Docker Compose:
```bash
make dev
# or: docker compose up --build
```

### Option 2: Running Separately (Without Docker)

#### Backend
First, ensure you have Python 3.12 installed.
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
*The API will be available at `http://localhost:8000` (and Swagger UI at `http://localhost:8000/docs`).*

#### Frontend
First, ensure you have Node.js installed.
```bash
cd frontend
npm install
npm run dev
```
*The frontend will be available at `http://localhost:5173`.*

> **💡 Pro Tip:** The root `Makefile` contains convenience scripts like `make run-be` and `make run-fe` to start these components as well.

### 🛠️ Available Make Commands

The project root includes a `Makefile` to simplify common operations. Here are all the commands at your disposal:

| Command | Description |
| :--- | :--- |
| `make dev` | Starts the Docker compose development environment (with hot-reloading). |
| `make prod` | Starts the Docker compose production environment. |
| `make clean` | Stops all containers and removes associated volumes. |
| `make logs` | Tails the logs for all Docker containers. |
| `make run-be` | Runs the FastAPI backend locally without Docker (requires `install-be`). |
| `make run-fe` | Runs the Vite frontend locally without Docker (requires `install-fe`). |
| `make install-be` | Installs Python dependencies via `pip` locally. |
| `make install-fe` | Installs Node dependencies via `npm` locally. |
| `make test` | Runs both backend and frontend test suites. |
| `make test-be` / `test-fe` | Runs individual backend or frontend test suites. |
| `make coverage` | Runs tests and generates a code coverage report. |
| `make lint` | Runs linters (Ruff/Black/ESLint) for both codebases. |
| `make lint-fix` | Attempts to auto-fix styling and linting issues. |
| `make help` | Prints the help menu with available commands directly in the terminal. |

---

## ⚙️ How it relates to DevOps

If you are exploring this codebase to learn DevOps, observe how the pieces fit together:
1.  **Code quality:** The Makefile ensures developers run tests locally.
2.  **Parity:** `docker-compose` ensures your laptop network mirrors the production network.
3.  **Automation:** The `.github/workflows` eliminate manual review of code style or functionality by strictly failing Pull Requests if tests break.
4.  **Immutability:** Docker images built on the staging pipeline are promoted, rather than recompiling code on actual servers.

---

## 📝 License

MIT License. Designed as a practical educational resource for modern DevOps pipelines.
