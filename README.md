# DSP Analyzer

A monorepo for DSP analysis tools.

![CI Python](https://github.com/user/repo/actions/workflows/ci-python.yml/badge.svg)
![CI Frontend](https://github.com/user/repo/actions/workflows/ci-frontend.yml/badge.svg)
![CI Rust](https://github.com/user/repo/actions/workflows/ci-rust.yml/badge.svg)

## Getting started

Prerequisites: Node 20, Rust (rustup), uv, Docker

### Setup

```bash
git clone ...
uv sync               # installs Python deps and creates .venv automatically
cd apps/desktop && npm install
```

### Development

```bash
npm run docker:up     # starts FastAPI on localhost:8000
npm run dev           # starts Tauri + Vue (separate terminal)
```

### Run Python tests only (for teammates who only work on core/dsp):
```bash
uv run pytest
uv run pytest core/dsp/tests/test_filters.py        # single file
uv run pytest -k "moving_average"                   # by test name
```