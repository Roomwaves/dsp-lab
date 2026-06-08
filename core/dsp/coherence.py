import numpy as np
import scipy.signal


def compute_psd(
    signal: np.ndarray,
    fs: float,
    n_segments: int = 8,
    window_size: int | None = None,
    overlap: float = 0.5,
    window_type: str = 'hann'
) -> tuple[np.ndarray, np.ndarray]:
    """
    Calcula la Densidad Espectral de Potencia (PSD) de una señal.
    Retorna (frecuencias, Gxx).
    """
    if window_size is not None:
        nperseg = min(len(signal), window_size)
        noverlap = int(nperseg * overlap)
        window = window_type
    else:
        n = len(signal)
        nperseg = max(1, n // n_segments)
        noverlap = nperseg // 2
        window = 'hann'
        
    freqs, Gxx = scipy.signal.welch(
        signal, fs=fs, window=window, nperseg=nperseg, noverlap=noverlap, scaling='density'
    )
    return freqs, Gxx

def compute_cpsd(
    x: np.ndarray,
    y: np.ndarray,
    fs: float,
    n_segments: int = 8,
    window_size: int | None = None,
    overlap: float = 0.5,
    window_type: str = 'hann'
) -> tuple[np.ndarray, np.ndarray]:
    """
    Calcula la Densidad Espectral de Potencia Cruzada (CPSD) entre dos señales.
    Retorna (frecuencias, Gxy_complejo).
    """
    if window_size is not None:
        nperseg = min(len(x), window_size)
        noverlap = int(nperseg * overlap)
        window = window_type
    else:
        n = len(x)
        nperseg = max(1, n // n_segments)
        noverlap = nperseg // 2
        window = 'hann'
        
    freqs, Gxy = scipy.signal.csd(
        x, y, fs=fs, window=window, nperseg=nperseg, noverlap=noverlap, scaling='density'
    )
    return freqs, Gxy

def compute_coherence(
    x: np.ndarray,
    y: np.ndarray,
    fs: float,
    n_segments: int = 8,
    window_size: int | None = None,
    overlap: float = 0.5,
    window_type: str = 'hann'
) -> tuple[np.ndarray, np.ndarray]:
    """
    Calcula la coherencia cuadrática entre dos señales.
    Retorna (frecuencias, coherencia_cuadratica).

    CORRECCIÓN DSP:
    Se reemplazó el uso directo de scipy.signal.coherence por un cálculo
    explícito basado en PSDs y CPSD:
    Cxy(f) = |Gxy(f)|^2 / (Gxx(f) * Gyy(f)).
    Para evitar divisiones por cero o valores indeterminados en regiones
    del espectro sin energía, se aplica un umbral inferior de 1e-12 al
    producto Gxx * Gyy. Los resultados son recortados en el rango [0.0, 1.0].
    """
    freqs, Gxx = compute_psd(
        x, fs, n_segments=n_segments, window_size=window_size, overlap=overlap, window_type=window_type
    )
    _, Gyy = compute_psd(
        y, fs, n_segments=n_segments, window_size=window_size, overlap=overlap, window_type=window_type
    )
    _, Gxy = compute_cpsd(
        x, y, fs, n_segments=n_segments, window_size=window_size, overlap=overlap, window_type=window_type
    )
    
    denom = Gxx * Gyy
    denom_safe = np.where(denom < 1e-12, 1e-12, denom)
    coh = (np.abs(Gxy) ** 2) / denom_safe
    
    return freqs, np.clip(coh, 0.0, 1.0)
