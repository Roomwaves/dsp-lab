# faculty/final/functions.py
# Academic Submission File — Entrega Final (Parte 2: Identificación de Sistemas y Coherencia).
# Re-exports and wraps functions from core/dsp.
# DO NOT duplicate core implementations here.

from core.dsp.analysis import (
    compute_fft,
    compute_frequency_response,
)
from core.dsp.coherence import compute_coherence
from core.dsp.filters import apply_fir
from core.dsp.io import load_audio, load_fir_coefficients
from core.dsp.plots import plot_coherence, plot_frequency_response
from core.dsp.signals import add_white_noise, generate_pure_tones


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
