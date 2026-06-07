import numpy as np


def compute_fft(signal: np.ndarray, fs: float) -> tuple[np.ndarray, np.ndarray]:
    """
    Calcula la Transformada de Fourier Discreta de una señal.
    Retorna (frecuencias, magnitudes).
    """
    n = len(signal)
    freqs = np.fft.rfftfreq(n, d=1/fs)
    mags = np.abs(np.fft.rfft(signal))
    return freqs, mags

def compute_frequency_response(x: np.ndarray, y: np.ndarray, fs: float) -> tuple[np.ndarray, np.ndarray]:
    """
    Calcula la respuesta en frecuencia H(w) = Y(w) / X(w).
    Retorna (frecuencias, H_complejo).
    """
    X = np.fft.rfft(x)
    Y = np.fft.rfft(y)
    denom = X.copy()
    denom[denom == 0] = 1e-15
    H = Y / denom
    freqs = np.fft.rfftfreq(len(x), d=1/fs)
    return freqs, H

def compute_magnitude_db(H: np.ndarray) -> np.ndarray:
    """
    Calcula el módulo de la respuesta en frecuencia en dB.
    """
    mag = np.abs(H)
    mag_db = np.zeros_like(mag)
    non_zero = mag > 0
    mag_db[non_zero] = 20.0 * np.log10(mag[non_zero])
    mag_db[~non_zero] = -120.0
    return mag_db

def compute_phase(H: np.ndarray) -> np.ndarray:
    """
    Calcula la fase de la respuesta en frecuencia en radianes.
    """
    return np.angle(H)

def convolve_time(signal: np.ndarray, h: np.ndarray) -> np.ndarray:
    """
    Realiza la convolución en el dominio del tiempo.
    """
    return np.convolve(signal, h, mode='full')

def convolve_frequency(signal: np.ndarray, h: np.ndarray) -> np.ndarray:
    """
    Realiza la convolución circular en el dominio de la frecuencia.
    """
    n_fft = len(signal) + len(h) - 1
    X = np.fft.fft(signal, n=n_fft)
    H = np.fft.fft(h, n=n_fft)
    Y = X * H
    y = np.fft.ifft(Y).real
    return y
