import numpy as np


def compute_fft(
    signal: np.ndarray,
    fs: float,
    window_size: int | None = None,
    overlap: float = 0.75,
    window_type: str = 'hann'
) -> tuple[np.ndarray, np.ndarray]:
    """
    Calcula la Transformada de Fourier Discreta de una señal.
    Retorna (frecuencias, magnitudes).
    Si window_size es provisto, realiza un promedio tipo Welch del espectro de amplitud
    (raíz cuadrada del PSD) para suavizar y reducir el ruido/resolución excesiva.
    De lo contrario, calcula la FFT completa clásica de la señal.
    """
    if window_size is not None:
        import scipy.signal
        nperseg = min(len(signal), window_size)
        noverlap = int(nperseg * overlap)
        freqs, Gxx = scipy.signal.welch(
            signal, fs=fs, window=window_type, nperseg=nperseg, noverlap=noverlap, scaling='spectrum'
        )
        # Tomamos la raíz de Gxx para obtener el espectro de amplitud promediado
        mags = np.sqrt(Gxx)
        return freqs, mags
    else:
        n = len(signal)
        freqs = np.fft.rfftfreq(n, d=1/fs)
        mags = np.abs(np.fft.rfft(signal))
        return freqs, mags

def compute_frequency_response(
    x: np.ndarray,
    y: np.ndarray,
    fs: float,
    window_size: int | None = None,
    overlap: float = 0.75,
    window_type: str = 'hann'
) -> tuple[np.ndarray, np.ndarray]:
    """
    Calcula la respuesta en frecuencia H(w) = Y(w) / X(w).
    Si window_size es provisto, usa el estimador H1 = Gxy / Gxx basado en el método de Welch
    para promediar segmentos y suavizar el ruido.
    De lo contrario, calcula H(w) = Y(w) / X(w) sobre la señal completa (con un umbral de seguridad).
    """
    if window_size is not None:
        import scipy.signal
        nperseg = min(len(x), window_size)
        noverlap = int(nperseg * overlap)
        
        freqs, Gxx = scipy.signal.welch(
            x, fs=fs, window=window_type, nperseg=nperseg, noverlap=noverlap, scaling='density'
        )
        _, Gxy = scipy.signal.csd(
            x, y, fs=fs, window=window_type, nperseg=nperseg, noverlap=noverlap, scaling='density'
        )
        
        # Umbral inferior de seguridad para Gxx
        threshold = 1e-12
        denom = Gxx.copy()
        zero_or_small = denom < threshold
        denom[zero_or_small] = threshold
        
        H = Gxy / denom
        return freqs, H
    else:
        X = np.fft.rfft(x)
        Y = np.fft.rfft(y)
        
        # Definimos un umbral inferior de seguridad para la magnitud de X(w)
        threshold = 1e-10
        
        # Creamos copia del denominador e inyectamos umbral con fase original
        denom = X.copy()
        zero_or_small = np.abs(X) < threshold
        
        # Para los valores críticos, fijamos una magnitud mínima sin alterar la fase
        denom[zero_or_small] = threshold * np.exp(
            1j * np.angle(X[zero_or_small])
        )
        
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
