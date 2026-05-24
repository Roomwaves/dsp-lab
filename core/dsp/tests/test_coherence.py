import numpy as np
import pytest
from core.dsp.coherence import compute_psd, compute_cpsd, compute_coherence

# --- Tests para Issue #8: PSD y CPSD ---

def test_psd_real_positive():
    """Gxx tiene valores reales y no negativos."""
    fs = 1000
    x = np.random.randn(1000)
    freqs, Gxx = compute_psd(x, fs)
    assert np.all(np.isreal(Gxx))
    assert np.all(Gxx >= 0.0)

def test_psd_frequency_range():
    """Frecuencias de 0 a <= fs/2."""
    fs = 1000
    x = np.random.randn(1000)
    freqs, Gxx = compute_psd(x, fs)
    assert freqs[0] == 0.0
    assert freqs[-1] <= fs / 2.0

def test_psd_lengths_match():
    """len(frequencies) == len(Gxx)."""
    fs = 1000
    x = np.random.randn(1000)
    freqs, Gxx = compute_psd(x, fs)
    assert len(freqs) == len(Gxx)

def test_cpsd_lengths_match():
    """len(frequencies) == len(Gxy)."""
    fs = 1000
    x = np.random.randn(1000)
    y = np.random.randn(1000)
    freqs, Gxy = compute_cpsd(x, y, fs)
    assert len(freqs) == len(Gxy)

def test_cpsd_same_signal():
    """Si x == y, entonces Gxy debe ser real y positiva (igual a PSD)."""
    fs = 1000
    x = np.random.randn(1000)
    freqs, Gxy = compute_cpsd(x, x, fs)
    freqs, Gxx = compute_psd(x, fs)
    np.testing.assert_allclose(Gxy, Gxx, rtol=1e-5)

def test_psd_white_noise_flat():
    """La PSD del ruido blanco debe ser aproximadamente plana."""
    fs = 10000
    x = np.random.randn(50000)
    freqs, Gxx = compute_psd(x, fs, n_segments=32)
    mean_val = np.mean(Gxx)
    # Con 32 segmentos, la desviación estándar debe ser menor al 80% de la media
    assert np.std(Gxx) < mean_val * 0.8

# --- Tests para Issue #9: Coherence ---

def test_coherence_range():
    """Todos los valores de coherence_sq están en [0, 1]."""
    fs = 1000
    x = np.random.randn(1000)
    y = np.random.randn(1000)
    freqs, coh = compute_coherence(x, y, fs)
    assert np.all(coh >= -1e-7)  # Permitir pequeños errores de precisión numérica
    assert np.all(coh <= 1.0 + 1e-7)

def test_coherence_identity():
    """Si y == x (sistema identidad), la coherencia es aprox 1 para todo w."""
    fs = 1000
    x = np.random.randn(1000)
    freqs, coh = compute_coherence(x, x, fs)
    np.testing.assert_allclose(coh, 1.0, rtol=1e-5)

def test_coherence_independent():
    """Si x e y son señales de ruido independientes, la coherencia es aprox 0."""
    fs = 10000
    x = np.random.randn(20000)
    y = np.random.randn(20000)
    freqs, coh = compute_coherence(x, y, fs, n_segments=32)
    # Promedio de coherencia entre señales independientes debería ser bajo
    assert np.mean(coh) < 0.3

def test_coherence_lengths_match():
    """len(frequencies) == len(coherence_sq)."""
    fs = 1000
    x = np.random.randn(1000)
    y = np.random.randn(1000)
    freqs, coh = compute_coherence(x, y, fs)
    assert len(freqs) == len(coh)

def test_coherence_real():
    """coherence_sq es real (no complejo)."""
    fs = 1000
    x = np.random.randn(1000)
    y = np.random.randn(1000)
    freqs, coh = compute_coherence(x, y, fs)
    assert np.all(np.isreal(coh))
