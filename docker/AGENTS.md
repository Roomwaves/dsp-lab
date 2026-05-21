# Development Environment

Docker Compose configuration for the local development environment.
**This directory is for development only — never for production deployment.**

---

## What runs here

```
docker-compose.yml    Orchestrates all dev services
api.dev.Dockerfile    Development image for FastAPI (with hot reload)
.env.example          Template for environment variables — copy to .env
```

The production FastAPI image lives in `apps/api/Dockerfile` and is bundled into
the Tauri binary at build time. The files here are only for `npm run docker:up`.

---

## Why Tauri does NOT run in Docker

Tauri requires access to the native OS webview (WebKit on macOS, WebView2 on Windows,
webkit2gtk on Linux). Running it inside a container would break native functionality.

**The split is:**
- Docker → API (and future services: database, Redis, etc.)
- Native → Tauri + Vue dev server (managed by `npm run dev`)

---

## Rules

### ✅ DO
- Mount source code as volumes so changes reflect without rebuild:
  ```yaml
  volumes:
    - ../apps/api:/app
    - ../core/dsp:/app/core/dsp
  ```
- Use `command: uv run uvicorn main:app --reload` for hot reload in dev
- Keep all configurable values in `.env` (port, debug flag, etc.)
- Add `.env` to `.gitignore` — only `.env.example` is committed
- Add new services (database, queue, etc.) as separate `services:` entries

### ❌ DON'T
- Use this `docker-compose.yml` as a production deployment config
- Hardcode ports or credentials in `docker-compose.yml` — use `${VAR}` substitution
- Build the Tauri app inside Docker
- Use `latest` tags for base images — pin to a specific version (e.g. `python:3.11-slim`)
- Run migrations or destructive operations in the dev compose without a confirmation step

---

## Environment variables

All configurable values live in `.env` (gitignored) based on `.env.example`:

```bash
# .env.example
API_PORT=8000
DEBUG=true
PYTHONPATH=/app
```

Access in `docker-compose.yml`:
```yaml
ports:
  - "${API_PORT:-8000}:8000"    # fallback to 8000 if not set
```

---

## Adding a new service

1. Add the service block to `docker-compose.yml`
2. Add any required env vars to `.env.example` (with example values)
3. Update the root `CLAUDE.md` commands section if the startup procedure changes
4. Document what the service does and why it's needed here in this file

---

## Commands

```bash
# From repo root
npm run docker:up        # Start all services (detached)
npm run docker:down      # Stop all services

# Direct compose commands (from docker/)
docker compose up                  # foreground (shows logs)
docker compose up --build          # force rebuild image
docker compose logs -f api         # follow API logs
docker compose exec api bash       # shell into the API container
docker compose run api uv run pytest  # run tests inside container
```
