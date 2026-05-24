import numpy as np
import pytest
from core.dsp.signals import generate_pure_tones, add_white_noise

# --- Tests para Issue #4: generate_pure_tones ---

def test_tones_output_length():
    """len(output) == int(fs * duration)"""
    fs = 1000
    duration = 2.5
    signal = generate_pure_tones([100], [1.0], fs, duration)
    assert len(signal) == int(fs * duration)

def test_tones_single_frequency():
    """Un tono puro a 440 Hz tiene su pico de FFT en 440 Hz."""
    fs = 4000
    duration = 1.0
    freq = 440.0
    signal = generate_pure_tones([freq], [1.0], fs, duration)
    # Calulamos FFT para verificar
    fft_vals = np.abs(np.fft.rfft(signal))
    fft_freqs = np.fft.rfftfreq(len(signal), 1/fs)
    peak_freq = fft_freqs[np.argmax(fft_vals)]
    assert np.abs(peak_freq - freq) < 2.0

def test_tones_amplitude_scaling():
    """Duplicar amplitud duplica la amplitud de la señal."""
    fs = 1000
    duration = 1.0
    s1 = generate_pure_tones([100], [1.0], fs, duration)
    s2 = generate_pure_tones([100], [2.0], fs, duration)
    np.testing.assert_allclose(s2, s1 * 2.0, rtol=1e-5)

def test_tones_zero_amplitude():
    """Amplitud 0 produce señal nula."""
    fs = 1000
    duration = 1.0
    signal = generate_pure_tones([100, 200], [0.0, 0.0], fs, duration)
    np.testing.assert_allclose(signal, 0.0, atol=1e-7)

# --- Tests para Issue #4: add_white_noise ---

def test_noise_snr_approximate():
    """La SNR medida empíricamente está dentro de ±2 dB de la pedida."""
    fs = 10000
    t = np.arange(10000) / fs
    clean = np.sin(2 * np.pi * 50 * t)
    
    snr_db = 15.0
    noisy = add_white_noise(clean, snr_db)
    
    noise = noisy - clean
    p_signal = np.mean(clean ** 2)
    p_noise = np.mean(noise ** 2)
    measured_snr_db = 10 * np.log10(p_signal / p_noise)
    
    assert np.abs(measured_snr_db - snr_db) < 2.0

def test_noise_output_length():
    """La longitud de salida es igual a la de entrada."""
    x = np.random.randn(100)
    y = add_white_noise(x, 10.0)
    assert len(y) == len(x)

def test_noise_different_each_call():
    """Dos llamadas seguidas producen resultados distintos (aleatoriedad real)."""
    x = np.ones(1000)
    y1 = add_white_noise(x, 10.0)
    y2 = add_white_noise(x, 10.0)
    assert not np.array_equal(y1, y2)
