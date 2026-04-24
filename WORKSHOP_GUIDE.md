# 🎙️ Presenter's Workshop Guide
**"A Day in the Life of a Developer" — DevOps Workshop Script**

This document is your step-by-step, spoon-fed guide to running the workshop. Follow these steps sequentially to perfectly demonstrate the entire lifecycle from local development, to Git, to automated testing, to GitHub Actions CI/CD.

---

## 🛑 Pre-Workshop Preparation
*Do this 30 minutes before the audience arrives.*

1.  **Open two Terminal windows:** Ensure they are both active in the `not_jenkins` directory.
2.  **Open an IDE:** Open this folder in VS Code or your preferred editor.
3.  **Prepare the GitHub Respository:** Have your repository open in the browser (`https://github.com/YOUR_USERNAME/not_jenkins`), specifically leaving a tab open on the **Actions** page.
4.  **Confirm Local Tools:** Ensure Docker Desktop is running (`docker info`). Ensure Python 3.12+ and Node 20+ are installed for local fast-running.

---

## 🎬 Part 1: The App Demo (0:00 - 0:10)
**Goal:** Show them the end-product so they know *what* we are building and testing.

**🗣️ Script / Actions:**
1.  *"Welcome! Today we are looking at a production-grade internal startup tool called FlowBoard. Before we dive into the operations, let's look at the app."*
2.  Go to **Terminal 1** and run:
    ```bash
    cp .env.example .env
    make dev
    ```
    *(Explain that `make dev` uses Docker Compose to instantly spin up both the FastAPI backend and the Vite frontend.)*
3.  Open `http://localhost:5173` in a browser.
4.  *"Notice the UI. It's a fully functioning task board."* Register a fake user (e.g., `user: admin`, `email: admin@test.com`, `pass: password123`).
5.  Create a board named "Workshop Tasks". Add a task "Setup CI/CD".
6.  Open `http://localhost:8000/docs` in another tab. *"This is our backend. Thanks to FastAPI, we have instant Swagger API documentation out of the box."*
7.  Hit `Ctrl+C` in the terminal to kill the app.

---

## 🎬 Part 2: The Codebase & Testing (0:10 - 0:20)
**Goal:** Explain that real code needs automated tests.

**🗣️ Script / Actions:**
1.  *"As developers, we don't just write code, we test it. We have a test suite written for both Python (pytest) and React (vitest)."*
2.  Go to **Terminal 1** and run:
    ```bash
    make test
    ```
3.  *"Watch how fast local tests run. In about 2 seconds, we just ran 38 backend tests validating our API and 10 frontend tests validating our UI. This is continuous feedback."*
4.  *"But what happens when developers collaborate? Let's talk about source control."* Open VS Code, and pull up the integrated terminal.
5.  Run `git log --oneline --graph --all`.
6.  *"Look at this beautiful graph. We have a `main` branch acting as our production code, a `dev` branch as our staging, and features branches where developers safely wrote this app without stepping on each other's toes."*

---

## 🎬 Part 3: Continuous Integration (CI) (0:20 - 0:35)
**Goal:** Prove that we can stop broken code from reaching the main branch.

**🗣️ Script / Actions:**
1.  *"We have local tests, but we can't trust that every developer runs them before pushing. This is where GitHub Actions steps in."*
2.  In VS Code, open `.github/workflows/ci.yml`.
3.  *Walk through the file:*
    *   *"It's triggered on any Pull Request."*
    *   *"Look at our jobs: `lint-backend`, `lint-frontend`, `test-backend`, `test-frontend`, `docker-build`."*
    *   *"Because they don't depend on each other, GitHub runs them concurrently. We save massive amounts of time."*
4.  Switch to your browser, go to your GitHub Repo -> **Actions tab**.
5.  Show a history of a successful workflow (if you push a dummy commit via a Pull Request to `dev`, you can show this live!). Point out the parallel execution graph.

---

## 🎬 Part 4: Continuous Deployment (CD) (0:35 - 0:50)
**Goal:** Show how code actually gets delivered to servers without human intervention.

**🗣️ Script / Actions:**
1.  *"Once CI passes and code merges, we deploy. Let's look at `.github/workflows/cd-staging.yml`."*
2.  In VS Code, highlight the `deploy-staging` step (around line 85).
3.  *"Notice what this workflow does. It authenticates with GitHub Container Registry, builds our Docker image, and tags it with the exact git commit SHA."*
4.  *"Then, we get to deployment."*
5.  **Important:** Explain to the audience that for the sake of presentation speed, you are using `echo` comments to simulate the deployment. Show them the commented-out `appleboy/ssh-action` block. *"In reality, GitHub Actions SSHs into your VM, pulls the Docker image it just built, and restarts the environment using `docker compose up -d`."*

---

## 🎬 Part 5: FAQ & Questions (0:50 - 1:00)

If the audience asks questions regarding deployment architecture:

### FAQ 1: Can GitHub Actions deploy a container locally on a different port?
**Example student question:** *"So GitHub Actions just creates the container, right? Instead of deploying it to a remote VM in the cloud, can it just map the container and deploy it onto our local machine on a different port?"*

**Your Answer:**
*"Yes, you absolutely can! By default, GitHub Actions runs your pipeline in a temporary, cloud-hosted runner provided by Microsoft. When the pipeline finishes, that server is destroyed. So, deploying it 'there' is only good for temporary smoke-tests.*

*However, GitHub has a feature called **Self-Hosted Runners**. You can install the GitHub Actions runner agent directly onto your local laptop or your company's own bare-metal server. If you do that, the workflow steps execute physically on your machine!*

*Since you control the machine, if your workflow runs:*
`docker run -d -p 8080:80 ghcr.io/my-image:latest`
*...then GitHub Actions will spin up that container on your actual local physical machine, safely mapped to port `8080` without any remote tunneling required!"*
