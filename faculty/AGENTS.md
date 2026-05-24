# Academic Deliverables

Jupyter notebooks and submission scripts for the university assignment
(Procesamiento Digital de Señales — "Filtrado e identificación de sistemas").

---

## Structure

```
faculty/
  preentrega/
    notebook.ipynb    Part 1: filter analysis, signal generation, convolution
    functions.py      Submission script (imports from core/dsp)
  final/
    notebook.ipynb    Part 2: system identification and coherence
    functions.py      Submission script (imports from core/dsp)
  datos/              Audio files and coefficient files provided by the professor
```

---

## Core rule

> **This directory imports from `core/dsp`. It never duplicates logic from it.**

```python
# CORRECT — import and use
from core.dsp.filters import moving_average, comb_filter, apply_fir
from core.dsp.signals import generate_impulse, generate_pure_tones, add_white_noise
from core.dsp.analysis import compute_fft, compute_frequency_response, convolve_time
from core.dsp.plots import plot_signal, plot_spectrum, plot_frequency_response

# WRONG — never copy-paste functions from core/dsp into the notebook
def moving_average(signal, M):     # ← don't do this
    ...
```

If something in `core/dsp` doesn't work as expected, fix it there — then the notebook picks up the fix automatically.

---

## Rules

### ✅ DO
- Use `Kernel → Restart & Run All` as the final check before any delivery — all cells must run clean
- Write conclusions in Markdown cells in plain prose — the professors evaluate the explanations, not the code
- Label every plot: title, X axis, Y axis, and legend when there are multiple curves
- Keep code cells short and focused — one concept per cell
- Reference the mathematical definitions from the assignment (`consigna`) in Markdown
- Use `functions.py` as the clean submission artifact that imports from `core/dsp`

### ❌ DON'T
- Call `plt.show()` inside the notebook — the Figure returned by plot functions displays inline automatically
- Store large audio arrays in the notebook output — clear outputs before committing (`Cell → All Output → Clear`)
- Hardcode absolute paths — use paths relative to the notebook file
- Commit the `datos/` folder if it contains copyrighted audio — add it to `.gitignore` if needed
- Fix bugs by editing the notebook — fix the function in `core/dsp` and re-run

---

## Notebook structure (pre-entrega)

Each section is owned by the person who implemented the corresponding function.

```
## 1. Respuesta al impulso de los filtros
   Code: generate_impulse() → each filter → plot h[n]
   Markdown: explain what impulse response means, describe each filter's shape

## 2. Caracterización en frecuencia
   Code: compute_frequency_response() → plot_frequency_response() for each filter
   Markdown: analyze magnitude and phase — is it low-pass, high-pass? Why?

## 3. Variación de parámetros
   Code: sweep M values [3, 8, 20] for MA; vary b0/b1/b2 for comb
   Markdown: describe the relationship between parameter values and frequency behavior

## 4. Señales de prueba
   Code: generate_pure_tones() + add_white_noise(), load_audio() + add_white_noise()
   Code: plot time domain and spectrum for clean vs noisy

## 5. Filtrado en tiempo y frecuencia
   Code: convolve_time() and convolve_frequency() — compare results
   Markdown: verify equivalence, comment on numerical differences if any

## 6. Truncado del FIR
   Code: apply_fir() with full coefficients vs truncate_fir(h, N) for N=[10, 50, 100]
   Markdown: describe the effect of truncation on the frequency response
```

---

## Notebook structure (entrega final)

```
## 1. Carga de señales de la cátedra
   Code: load_audio() for input/output pairs from datos/

## 2. Identificación de H(ω)
   Code: compute_frequency_response(x, y, fs) → plot_frequency_response()
   Markdown: what type of system does it appear to be?

## 3. Coherencia cuadrática
   Code: compute_coherence(x, y, fs) → plot_coherence()
   Markdown: answer the three questions from the assignment (copy them verbatim and respond below each)

## 4. Conclusión
   Markdown: integrating analysis of linearity across the spectrum
```

**The three required questions from the assignment:**
1. ¿Por qué la coherencia vale 1 cuando la relación es perfectamente lineal, dada la forma en que se calcula?
2. ¿Cómo es la linealidad del sistema en distintas partes del espectro?
3. ¿Qué tipos de sistemas físicos reales podrían dar lugar a ese comportamiento?

---

## functions.py format

The professor requires a standalone `.py` file. Use imports from `core/dsp`:

```python
# faculty/preentrega/functions.py
# Submission file — re-exports functions from core/dsp for the academic delivery.
# DO NOT duplicate any implementation here.

from core.dsp.filters import moving_average, comb_filter, apply_fir, truncate_fir
from core.dsp.analysis import (
    compute_fft,
    compute_frequency_response,
    compute_magnitude_db,
    compute_phase,
    convolve_time,
    convolve_frequency,
)
from core.dsp.signals import generate_pure_tones, add_white_noise, generate_impulse
from core.dsp.coherence import compute_psd, compute_cpsd, compute_coherence
from core.dsp.io import load_audio, save_audio, load_fir_coefficients
from core.dsp.plots import plot_signal, plot_spectrum, plot_frequency_response, plot_coherence
```

If the professor requires a truly self-contained file with no imports from `core/`,
copy the implementations at delivery time — but never maintain two versions in parallel.

---

## Delivery checklist

- [ ] `Kernel → Restart & Run All` passes without errors
- [ ] Every section has at least one Markdown cell with written conclusions
- [ ] All plots have title, axis labels, and legend (where applicable)
- [ ] `functions.py` exists and can be imported without errors
- [ ] No large binary files committed (audio files go in `datos/`, not in the notebook outputs)
