# DSP Engine (Python)

Pure Python DSP logic. This is the mathematical heart of the project.
Everything here must be importable standalone — no FastAPI, no Tauri, no HTTP.

---

## Module structure

```
filters.py      Moving average, comb filter, FIR — batch and stateful classes
analysis.py     FFT, frequency response H(ω), convolution (time and frequency)
signals.py      Signal generators: pure tones, white noise, impulse
coherence.py    PSD, CPSD, quadratic coherence γ²xy(ω)
io.py           Audio file I/O (load/save .wav) and coefficient loading
plots.py        Visualization — all functions return Figure, never call plt.show()
tests/          Pytest test suite — tests are already written, make them pass
```

**Each file owns exactly one domain. Do not mix concerns.**
If a function needs both filter logic and FFT: it lives in `analysis.py` and imports from `filters.py`.

---

## Rules

### ✅ DO
- Import numpy and scipy freely — they are the standard tools here
- Return `np.ndarray` from all computational functions
- Return `matplotlib.figure.Figure` from all plot functions
- Raise `ValueError` with a descriptive message for invalid inputs
- Write docstrings with: purpose, args, returns, mathematical definition, and a usage example
- Keep functions pure (same input → same output, no side effects)
- Use `np.random.default_rng(seed)` with explicit seeds in tests, never `np.random.seed()` globally
- Add type hints to all function signatures
- Add the stateful class whenever you implement a filter (see pattern below)

### ❌ DON'T
- Import `fastapi`, `uvicorn`, `httpx`, or any HTTP library
- Import from `apps/` — this module has no knowledge of the API or UI
- Call `plt.show()` or `plt.savefig()` inside any function — return the Figure instead
- Use `print()` for debugging — use proper logging or remove before committing
- Hardcode file paths — `io.py` receives `filepath` as argument
- Store state in module-level variables — stateful behavior lives in classes
- Use `np.random.seed()` globally — use `np.random.default_rng(seed)` locally
- Use float32 as the default dtype — all math is float64; document f32 compatibility separately

---

## Two-tier API: batch and stateful

Every filter must have both versions:

```python
# 1. Batch — processes whole signal at once (used in TP notebooks)
def moving_average(signal: np.ndarray, M: int, passes: int = 1) -> np.ndarray:
    ...

# 2. Stateful — processes one block at a time (used in real-time Rust port)
class MovingAverageFilter:
    def __init__(self, M: int) -> None:
        self._buffer = np.zeros(M - 1)   # persists between blocks

    def process_block(self, block: np.ndarray) -> np.ndarray:
        ...

    def reset(self) -> None:
        self._buffer = np.zeros(self.M - 1)
```

The stateful class mirrors what the Rust implementation will do.
`process_block()` must produce the same result as the batch version
when called sequentially (verified by `test_block_consistency_with_batch`).

---

## Function signature conventions

```python
# Computational functions
def compute_fft(signal: np.ndarray, fs: float) -> tuple[np.ndarray, np.ndarray]:
    """Returns (frequencies, magnitudes)."""

# Plot functions — always accept optional ax/fig to allow subplot composition
def plot_signal(
    signal: np.ndarray,
    fs: float,
    title: str = "Signal",
    ax: plt.Axes | None = None,
) -> matplotlib.figure.Figure:
    ...
```

---

## Error handling

```python
# Validate inputs at the top of the function, before any computation
def moving_average(signal: np.ndarray, M: int, passes: int = 1) -> np.ndarray:
    if M < 1:
        raise ValueError(f"M must be >= 1, got {M}")
    if not 1 <= passes <= 3:
        raise ValueError(f"passes must be 1, 2 or 3, got {passes}")
    if len(signal) < M:
        raise ValueError(f"signal length ({len(signal)}) must be >= M ({M})")
    ...
```

---

## Tests

Tests live in `tests/` and are **already written**. Your job is to make them pass.

```bash
# Run all DSP tests
uv run pytest core/dsp/tests/

# Run a single file
uv run pytest core/dsp/tests/test_filters.py

# Run a specific test
uv run pytest -k "test_dc_preservation"

# Run with verbose output
uv run pytest core/dsp/tests/ -v
```

**Do not modify tests to make them pass. Fix the implementation instead.**
If a test seems wrong, open a discussion — don't silently change it.

Test classes map 1:1 to functions:
- `TestMovingAverage` → `moving_average()`
- `TestMovingAverageFilter` → `MovingAverageFilter`
- `TestCombFilter` → `comb_filter()`
- etc.

---

## Adding a new function

1. Add the stub (signature + docstring + `raise NotImplementedError`) to the correct file
2. Add it to `__init__.py` exports
3. Add tests in the corresponding `test_*.py` file
4. Implement until all tests pass
5. Open PR to `dev`

---

## Integration with other modules

| Who imports from here | What they use |
|-----------------------|---------------|
| `apps/api/routes/`    | All computational functions |
| `faculty/`            | All computational functions |
| `core/dsp_rs/tests/`  | Fixture files generated by `scripts/generate_rust_fixtures.py` |

`core/dsp` imports from **nobody** inside this repo.
