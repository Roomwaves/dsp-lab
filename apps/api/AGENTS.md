# FastAPI Sidecar

Thin HTTP layer that exposes `core/dsp` over a REST API.
This process runs as a sidecar alongside the Tauri desktop app.

---

## Core principle

> **This module contains zero DSP logic.**

Every route handler must:
1. Parse and validate the request body (Pydantic)
2. Call one or more functions from `core/dsp`
3. Return the result

If you find yourself writing numpy operations in a route handler, stop — move that logic to `core/dsp` instead.

---

## Module structure

```
routes/
  filters.py      POST /filters/apply, POST /filters/impulse-response
  analysis.py     POST /analysis/fft, POST /analysis/frequency-response
  coherence.py    POST /coherence
  io.py           POST /io/load-audio (multipart upload)
schemas/
  signal.py       SignalInput, SignalOutput, FrequencyResponseOutput, ...
  filter.py       FilterParams, MovingAverageParams, CombFilterParams, FIRParams
  coherence.py    CoherenceInput, CoherenceOutput
main.py           App factory, router mounting, CORS, /health
```

Routes mirror `core/dsp` modules 1:1.
Adding a new DSP function → add the function to `core/dsp` first, then add the route here.

---

## Rules

### ✅ DO
- Use Pydantic models for all request and response bodies — no raw `dict`
- Delegate all computation to `core/dsp` functions
- Return structured JSON responses (Pydantic `model.model_dump()`)
- Use `HTTPException` for client errors (400, 422) and let FastAPI handle 500s
- Keep route handlers under ~15 lines of logic
- Version routes if breaking changes are needed: `/v1/filters/apply`
- Use `from core.dsp import ...` — never use relative imports across packages

### ❌ DON'T
- Import `numpy`, `scipy`, or `matplotlib` directly in routes — that's `core/dsp`'s job
- Store state between requests — this API is stateless
- Hardcode the port — it comes from the `API_PORT` env var
- Add authentication logic here — this API is local-only (localhost)
- Return raw numpy arrays — serialize to Python lists via `.tolist()`
- Commit `.env` files — use `.env.example` as the template

---

## Schema conventions

Arrays travel as JSON lists. Pydantic handles the conversion:

```python
# schemas/signal.py
from pydantic import BaseModel, Field

class SignalInput(BaseModel):
    samples: list[float] = Field(..., description="Signal samples x[n]")
    fs: float = Field(..., gt=0, description="Sample rate in Hz")

class FFTOutput(BaseModel):
    frequencies: list[float]
    magnitudes: list[float]
```

**Always validate constraints in the schema (e.g. `gt=0`, `ge=1`) — not in the route handler.**

---

## Route handler pattern

```python
# routes/analysis.py
from fastapi import APIRouter, HTTPException
from core.dsp.analysis import compute_fft
from ..schemas.signal import SignalInput, FFTOutput

router = APIRouter(prefix="/analysis", tags=["analysis"])

@router.post("/fft", response_model=FFTOutput)
def fft_endpoint(body: SignalInput) -> FFTOutput:
    signal = np.array(body.samples)
    frequencies, magnitudes = compute_fft(signal, fs=body.fs)
    return FFTOutput(
        frequencies=frequencies.tolist(),
        magnitudes=magnitudes.tolist(),
    )
```

---

## CORS

CORS is configured in `main.py` to allow only `localhost` origins.
Do not open it to `*` — this API is not meant to be public.

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:1420"],  # Tauri dev port
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)
```

---

## Health check

`GET /health` must always return `{"status": "ok"}`.
Tauri checks this endpoint on startup to confirm the sidecar is ready.

---

## Adding a new endpoint

1. Add the DSP function to `core/dsp/` (if not there yet)
2. Add/update the Pydantic schema in `schemas/`
3. Add the route handler in the appropriate `routes/*.py`
4. Mount the router in `main.py` (if new file)
5. Test with `curl` or the auto-generated docs at `localhost:8000/docs`

---

## Commands

```bash
# Start for development (from repo root)
npm run docker:up

# Start without Docker (requires .venv active)
uv run uvicorn apps.api.main:app --reload --port 8000

# API docs (while running)
open http://localhost:8000/docs
```
