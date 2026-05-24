import numpy as np
import pytest
from core.dsp.analysis import (
    compute_fft,
    compute_frequency_response,
    compute_magnitude_db,
    compute_phase,
    convolve_time,
    convolve_frequency
)

# --- Tests para Issue #5: compute_fft ---

def test_fft_dc_signal():
    """Una señal constante tiene toda su energía en f=0."""
    fs = 1000
    x = np.ones(1000)
    freqs, mags = compute_fft(x, fs)
    assert np.argmax(mags) == 0

def test_fft_sine_peak():
    """Un seno a 440 Hz tiene su pico en el bin más cercano a 440 Hz."""
    fs = 4000
    t = np.arange(4000) / fs
    x = np.sin(2 * np.pi * 440 * t)
    freqs, mags = compute_fft(x, fs)
    peak_freq = freqs[np.argmax(mags)]
    assert np.abs(peak_freq - 440.0) < 2.0

def test_fft_frequency_range():
    """frequencies[0] == 0 y frequencies[-1] <= fs/2."""
    fs = 1000
    x = np.random.randn(100)
    freqs, mags = compute_fft(x, fs)
    assert freqs[0] == 0.0
    assert freqs[-1] <= fs / 2.0

def test_fft_lengths_match():
    """len(frequencies) == len(magnitudes)."""
    fs = 1000
    x = np.random.randn(100)
    freqs, mags = compute_fft(x, fs)
    assert len(freqs) == len(mags)

def test_fft_positive_magnitudes():
    """Todos los valores de magnitudes son >= 0."""
    fs = 1000
    x = np.random.randn(100)
    freqs, mags = compute_fft(x, fs)
    assert np.all(mags >= 0.0)

def test_fft_nyquist():
    """La frecuencia máxima retornada no supera fs/2."""
    fs = 1000
    x = np.random.randn(100)
    freqs, mags = compute_fft(x, fs)
    assert freqs[-1] <= fs / 2.0


# --- Tests para Issue #6: frequency response ---

def test_freq_response_identity_system():
    """Si y == x, entonces |H(w)| aprox 1 para todo w."""
    fs = 1000
    x = np.random.randn(1000)
    freqs, H = compute_frequency_response(x, x, fs)
    np.testing.assert_allclose(np.abs(H), 1.0, rtol=1e-5)

def test_freq_response_lengths_match():
    """len(frequencies) == len(H)."""
    fs = 1000
    x = np.random.randn(100)
    y = np.random.randn(100)
    freqs, H = compute_frequency_response(x, y, fs)
    assert len(freqs) == len(H)

def test_freq_response_complex():
    """H tiene dtype complejo."""
    fs = 1000
    x = np.random.randn(100)
    y = np.random.randn(100)
    freqs, H = compute_frequency_response(x, y, fs)
    assert np.iscomplexobj(H)

def test_magnitude_db_units():
    """Para H=1 (sistema identidad), la magnitud en dB es 0 dB."""
    H = np.array([1.0, 10.0, 0.1, 0.0])
    mag_db = compute_magnitude_db(H)
    assert np.abs(mag_db[0] - 0.0) < 1e-5
    assert np.abs(mag_db[1] - 20.0) < 1e-5
    assert np.abs(mag_db[2] - (-20.0)) < 1e-5

def test_phase_range():
    """Los valores de fase están en [-pi, pi]."""
    H = np.array([1+1j, -1-1j, 1-1j, -1+1j])
    phase = compute_phase(H)
    assert np.all(phase >= -np.pi)
    assert np.all(phase <= np.pi)

def test_freq_response_frequency_range():
    """Las frecuencias van de 0 a <= fs/2."""
    fs = 1000
    x = np.random.randn(100)
    y = np.random.randn(100)
    freqs, H = compute_frequency_response(x, y, fs)
    assert freqs[0] == 0.0
    assert freqs[-1] <= fs / 2.0


# --- Tests para Issue #7: convolve ---

def test_convolve_time_output_length():
    """len(y) == len(signal) + len(h) - 1."""
    x = np.random.randn(50)
    h = np.random.randn(10)
    y = convolve_time(x, h)
    assert len(y) == len(x) + len(h) - 1

def test_convolve_freq_output_length():
    """len(y) == len(signal) + len(h) - 1."""
    x = np.random.randn(50)
    h = np.random.randn(10)
    y = convolve_frequency(x, h)
    assert len(y) == len(x) + len(h) - 1

def test_convolve_equivalence():
    """Ambas funciones producen resultados casi idénticos."""
    x = np.random.randn(100)
    h = np.random.randn(15)
    y1 = convolve_time(x, h)
    y2 = convolve_frequency(x, h)
    np.testing.assert_allclose(y1, y2, atol=1e-10)

def test_convolve_time_delta():
    """Convolucionar con d[n] reproduce la señal original."""
    x = np.random.randn(50)
    h = np.array([1.0])
    y = convolve_time(x, h)
    np.testing.assert_allclose(y, x)

def test_convolve_freq_delta():
    """Convolucionar con d[n] reproduce la señal original."""
    x = np.random.randn(50)
    h = np.array([1.0])
    y = convolve_frequency(x, h)
    np.testing.assert_allclose(y, x)
