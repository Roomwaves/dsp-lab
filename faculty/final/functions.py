# faculty/final/functions.py
# Academic Submission File — Entrega Final (Parte 2: Identificación de Sistemas y Coherencia).
# Re-exports and wraps functions from core/dsp.
# DO NOT duplicate core implementations here.

import sys
from pathlib import Path

_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from core.dsp.analysis import (  # noqa: E402
    compute_fft,
    compute_frequency_response,
    convolve_frequency,
    convolve_time,
)
from core.dsp.coherence import compute_coherence  # noqa: E402
from core.dsp.filters import (  # noqa: E402
    apply_fir,
    comb_filter,
    moving_average,
    truncate_fir,
)
from core.dsp.io import load_audio, load_fir_coefficients  # noqa: E402
from core.dsp.plots import (  # noqa: E402
    plot_coherence,
    plot_frequency_response,
    plot_signal,
    plot_spectrum,
)
from core.dsp.signals import (  # noqa: E402
    add_white_noise,
    generate_impulse,
    generate_pure_tones,
)
from faculty.preentrega.functions import (  # noqa: E402
    filtrar_frecuencia_manual,
    filtro_fir,
    filtro_media_movil,
    filtro_peine,
    graficar_frecuencias,
    graficar_temp,
    rta_frecuencia,
    suma_musical,
    suma_tonos_puros,
)


def identificar_sistema(x, y, fs=44100, window_size=1024):
    """
    Calcula la respuesta en frecuencia estimador H1 = Gxy / Gxx
    utilizando promediado Welch para suavizar el ruido.
    """
    freqs, H = compute_frequency_response(x, y, fs=fs, window_size=window_size)
    return freqs, H


def evaluar_coherencia(x, y, fs=44100, window_size=1024):
    """
    Calcula la coherencia cuadrática gamma_xy^2(w) = |Gxy|^2 / (Gxx * Gyy)
    para analizar la linealidad entre la entrada x y la salida y.
    """
    freqs, coh = compute_coherence(x, y, fs=fs, window_size=window_size)
    return freqs, coh


__all__ = [
    "compute_fft",
    "compute_frequency_response",
    "compute_coherence",
    "convolve_frequency",
    "convolve_time",
    "apply_fir",
    "truncate_fir",
    "comb_filter",
    "moving_average",
    "load_audio",
    "load_fir_coefficients",
    "plot_coherence",
    "plot_frequency_response",
    "plot_signal",
    "plot_spectrum",
    "add_white_noise",
    "generate_impulse",
    "generate_pure_tones",
    "identificar_sistema",
    "evaluar_coherencia",
    "graficar_temp",
    "graficar_frecuencias",
    "rta_frecuencia",
    "suma_tonos_puros",
    "suma_musical",
    "filtro_media_movil",
    "filtro_peine",
    "filtro_fir",
    "filtrar_frecuencia_manual",
]


if __name__ == "__main__":
    print("Corriendo pruebas locales en faculty/final/functions.py...")
    import numpy as np

    fs = 44100
    dur = 2.0
    x = np.random.normal(0, 1, int(fs * dur))
    # Sistema LTI ideal con ruido aditivo
    y = np.convolve(x, [0.5, 0.3, 0.2], mode="full")[: len(x)] + 0.1 * np.random.normal(0, 1, len(x))

    freqs, H = identificar_sistema(x, y, fs=fs)
    freqs, coh = evaluar_coherencia(x, y, fs=fs)

    print(f"Respuesta H de longitud {len(H)}, Coherencia de longitud {len(coh)}")
    print("Prueba completada exitosamente.")
