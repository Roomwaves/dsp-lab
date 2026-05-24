# DSP Analyzer — Root

Monorepo for a cross-platform DSP analysis desktop application.
Combines a Python DSP engine, a FastAPI sidecar, and a native Tauri + Vue UI.

> Each subdirectory has its own `AGENTS.md` with module-specific rules.
> **Always read the relevant `AGENTS.md` before modifying code in that directory.**

---

## Repository map

```
core/dsp/          Python DSP engine — pure math, no I/O, no HTTP
core/dsp_rs/       Rust DSP engine — real-time, block-based mirror of core/dsp
apps/api/          FastAPI sidecar — thin HTTP layer over core/dsp
apps/desktop/      Tauri + Vue desktop app — UI only
faculty/           Academic deliverables — notebooks + submission scripts
docker/            Dev-only Docker configuration
```

## Where does new code go?

| What you're adding | Where it lives |
|--------------------|----------------|
| DSP algorithm (filter, FFT, analysis) | `core/dsp/` |
| Same algorithm optimized for real-time | `core/dsp_rs/` |
| New API endpoint | `apps/api/routes/` |
| New UI panel or tool | `apps/desktop/src/` |
| TP notebook section | `faculty/` |
| Dev infrastructure | `docker/` |

**Never put DSP math in `apps/api/`.
Never put HTTP logic in `core/dsp/`.
Never duplicate logic across modules — import it.**

---

## Cross-cutting rules

### No hardcoding
- Ports, paths, URLs → environment variables or config files
- `API_PORT` lives in `docker/.env.example`, read via `os.getenv()`
- Magic numbers in DSP (e.g. sample rate default) → named constants at the top of the file, never inline

### Single Responsibility
- One file = one domain. `filters.py` only has filters. `analysis.py` only has analysis.
- If a function needs to import from two different modules in `core/dsp/`, reconsider the design.

### No global mutable state
- No module-level variables that change at runtime
- DSP state lives in stateful classes (`MovingAverageFilter`, etc.), not global vars
- Pinia stores manage UI state in the frontend, not component `data`

### Dependency direction (strictly enforced)
```
apps/desktop  →  apps/api  →  core/dsp
                              core/dsp_rs (via Tauri commands)
faculty       →  core/dsp
```
Arrows point in one direction only. `core/dsp` knows nothing about FastAPI or Vue.

---

## Tech stack quick reference

| Layer | Language | Key tools |
|-------|----------|-----------|
| DSP core | Python 3.11 | numpy, scipy, matplotlib |
| DSP real-time | Rust | rustfft, cpal (future) |
| API | Python 3.11 | FastAPI, Pydantic, uvicorn |
| Desktop shell | Rust | Tauri v2 |
| Desktop UI | TypeScript | Vue 3, Vite, Pinia |
| Package mgmt (Python) | — | uv + pyproject.toml |
| Package mgmt (JS) | — | npm |

---

## Commands

```bash
# Setup (run once after clone)
uv sync
cd apps/desktop && npm install

# Development
npm run docker:up     # FastAPI on localhost:8000
npm run dev           # Tauri + Vue (separate terminal)

# Testing
npm run test:all      # Python + frontend
npm run test:python   # uv run pytest
npm run test:frontend # cd apps/desktop && npx vitest run

# Linting
npm run lint:python   # ruff check .
npm run lint:frontend # cd apps/desktop && npm run lint
```

---

## Git conventions

- Branches: `feat/`, `fix/`, `docs/`, `test/`, `chore/`
- Commits: `feat:`, `fix:`, `docs:`, `test:`, `chore:` prefixes
- All work goes to `feat/*` → PR to `dev` → `main` only for releases
- `main` is protected: no direct pushes
