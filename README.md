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

## 🏃 Workshop Demo Guide

Here are the step-by-step instructions to follow during your demo workshop:

### 1. Show the Application Running Locally

We provide two easy ways to run the app. **Docker is recommended** for the demo.

**Method A: Using Docker (Recommended for Demo)**
Open a terminal in the project root:
```bash
# 1. Copy the environment variables template
cp .env.example .env

# 2. Build and start the containers using the Makefile
make dev
```
*   The frontend will be available at: `http://localhost:5173`
*   The backend API will be at: `http://localhost:8000`
*   The Swagger API docs will be at: `http://localhost:8000/docs`

**Method B: Without Docker (Local Services)**
Open two separate terminals in the project root.
Terminal 1 (Backend):
```bash
make install-be
make run-be
```
Terminal 2 (Frontend):
```bash
make install-fe
make run-fe
```

Show the audience the login screen, create an account, create a board, and add some tasks to show the application working!

### 2. Show the Test Suites

A vital part of the developer lifecycle is automated testing. Show the tests running locally:
```bash
# Run both Frontend and Backend tests seamlessly
make test
```
*   *(Expect to see 38 backend Pytest tests pass and 10 frontend Vitest tests pass in seconds!)*

### 3. Show Git Branching Mechanics

Show the audience how the project was structured using Git:
```bash
# Show a visual tree of the branches and commits
git log --oneline --graph --all
```
Explain the strategy:
*   `main`: The production-ready code.
*   `dev`: The staging integration branch.
*   `feature/auth` & `feature/ui`: The individual branches developers worked on to build the app.

---

## ⚙️ GitHub Setup & CI/CD Pipelines

The project includes three full CI/CD workflows under `.github/workflows/`. Before the workshop, you need to set up the repository on GitHub.

### 1. Repository Setup
1. Create a new repository on GitHub.
2. Push this local directory to the remote:
```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git push -u origin main
git push origin dev
```

### 2. The Pipelines Explained

During the workshop, navigate to the **Actions** tab on your GitHub repository to show the pipelines running:

1.  **CI (Continuous Integration)** (`ci.yml`):
    *   **Triggers:** On any Pull Request aiming for `main` or `dev`.
    *   **What it does:** Runs 5 parallel jobs! It lints backend and frontend, tests both with code coverage, and does a dry-run Docker build to ensure the images will build successfully.
2.  **CD Staging** (`cd-staging.yml`):
    *   **Triggers:** Automatically when code is merged or pushed to the `dev` branch.
    *   **What it does:** Runs tests again, builds real Docker images, tags them with the git commit SHA, pushes them to GitHub Container Registry (GHCR), and simulates an SSH deployment to a staging server.
3.  **CD Production** (`cd-production.yml`):
    *   **Triggers:** Automatically when code is merged into `main`.
    *   **What it does:** Similar to staging, but tags images with semantic versions AND pauses to wait for manual approval using a GitHub Environment before deploying to "production".

### 3. Where is Deployment Happening?

For the purpose of ensuring the workshop is seamless and has zero friction, **the deployment steps in the workflows are currently *simulated***.

If you inspect `cd-staging.yml` and `cd-production.yml` on lines `95+` and `103+` respectively, you will see `echo` commands simulating SSH connections and Docker pull commands. This safely demonstrates *how* deployment works without requiring you to buy, configure, and debug a live AWS EC2 or DigitalOcean droplet mid-workshop. 

The Docker images, however, are *actually* built and pushed to GitHub Container Registry (GHCR).

---

## FAQ: Changing GitHub Actions Deployment Ports

**Question:** *Can we use GitHub Actions to deploy the application on a different port?*

**Answer:** *Yes, absolutely! GitHub Actions itself doesn't lock you into any port. It just runs the deployment commands.*

If your deployment server is using Docker Compose (like our simulated production deploy), you control the exposed port inside `docker-compose.prod.yml`.

For example, if you wanted the application to run on port `8080` instead of port `80` on the server, you would simply modify the `nginx` service in `docker-compose.prod.yml`:

```yaml
# docker-compose.prod.yml
services:
  nginx:
    image: nginx:1.27-alpine
    container_name: flowboard-nginx
    # Changing the host port mapping from "80:80" to "8080:80"
    ports:
      - "8080:80" 
```

When GitHub Actions executes the `docker compose up` command on your server, Docker automatically handles exposing it locally on `8080`.

---

## 🏗️ Tech Stack

**Backend:** FastAPI · Python 3.12 · JWT Auth · In-memory store (DB-ready)  
**Frontend:** React 18 · Vite · TypeScript · Dark glassmorphism UI  
**DevOps:** Docker · Docker Compose · GitHub Actions · GHCR  

---

## 📁 Project Structure

```text
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

## 📝 License

MIT — built for education purposes as part of the DevOps Workshop series.
