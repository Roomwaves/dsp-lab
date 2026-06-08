import numpy as np
import scipy.signal


def generate_pure_tones(
    frequencies: list[float], amplitudes: list[float], fs: float, duration: float
) -> np.ndarray:
    """
    Genera una señal suma de tonos puros.
    """
    if len(frequencies) != len(amplitudes):
        raise ValueError("frequencies and amplitudes must have the same length")
    num_samples = int(fs * duration)
    t = np.arange(num_samples) / fs
    signal = np.zeros(num_samples)
    for f, a in zip(frequencies, amplitudes):
        signal += a * np.sin(2 * np.pi * f * t)
    return signal


def generate_square_wave(
    frequency: float, amplitude: float, fs: float, duration: float, duty: float = 0.5
) -> np.ndarray:
    """
    Genera una onda cuadrada con la frecuencia, amplitud,
    tasa de muestreo y duración especificadas.
    El parámetro duty controla el ciclo de trabajo (entre 0.0 y 1.0, por defecto 0.5).
    """
    num_samples = int(fs * duration)
    t = np.arange(num_samples) / fs
    return amplitude * scipy.signal.square(2 * np.pi * frequency * t, duty=duty)


def generate_triangle_wave(
    frequency: float, amplitude: float, fs: float, duration: float, width: float = 0.5
) -> np.ndarray:
    """
    Genera una onda triangular (o diente de sierra si width != 0.5) con la
    frecuencia, amplitud, tasa de muestreo y duración especificadas.
    El parámetro width controla dónde ocurre el pico (por defecto 0.5).
    """
    num_samples = int(fs * duration)
    t = np.arange(num_samples) / fs
    return amplitude * scipy.signal.sawtooth(2 * np.pi * frequency * t, width=width)


def generate_white_noise(
    amplitude: float, fs: float, duration: float, gaussian: bool = False
) -> np.ndarray:
    """
    Genera ruido blanco.
    Si gaussian=True, usa distribución normal (amplitud como desviación estándar).
    Si gaussian=False, usa distribución uniforme entre -amplitud y +amplitud.
    """
    num_samples = int(fs * duration)
    if gaussian:
        return np.random.normal(0.0, amplitude, num_samples)
    else:
        return np.random.uniform(-amplitude, amplitude, num_samples)


def generate_pink_noise(amplitude: float, fs: float, duration: float) -> np.ndarray:
    """
    Genera ruido rosa (decaimiento de 3 dB/octava o 1/f) filtrando
    ruido blanco en el dominio frecuencial.
    """
    num_samples = int(fs * duration)
    if num_samples <= 0:
        return np.zeros(0)
    white = np.random.normal(0.0, 1.0, num_samples)
    white_fft = np.fft.rfft(white)
    frequencies = np.fft.rfftfreq(num_samples, d=1.0 / fs)

    with np.errstate(divide="ignore", invalid="ignore"):
        filter_mag = 1.0 / np.sqrt(frequencies)
    filter_mag[0] = 0.0  # Eliminar componente continua (DC)

    pink_fft = white_fft * filter_mag
    pink = np.fft.irfft(pink_fft, n=num_samples)

    pink = pink - np.mean(pink)
    max_val = np.max(np.abs(pink))
    if max_val > 0:
        pink = (pink / max_val) * amplitude
    return pink


def generate_sweep(
    f_start: float,
    f_end: float,
    sweep_type: str,
    amplitude: float,
    fs: float,
    duration: float,
) -> np.ndarray:
    """
    Genera un barrido de frecuencia (sweep/chirp) lineal o logarítmico.
    """
    num_samples = int(fs * duration)
    t = np.arange(num_samples) / fs

    if sweep_type == "linear":
        phase = 2 * np.pi * (f_start * t + 0.5 * (f_end - f_start) * (t**2) / duration)
    elif sweep_type == "logarithmic":
        if f_start <= 0 or f_end <= 0:
            raise ValueError(
                "Start and end frequencies must be positive for logarithmic sweep"
            )
        k = np.log(f_end / f_start)
        phase = 2 * np.pi * f_start * duration / k * (np.exp(k * t / duration) - 1)
    else:
        raise ValueError(f"Unknown sweep type: {sweep_type}")

    return amplitude * np.sin(phase)


def add_white_noise(signal: np.ndarray, snr_db: float) -> np.ndarray:
    """
    Agrega ruido blanco a la señal para alcanzar una SNR especificada en dB.
    """
    p_signal = np.mean(signal**2)
    if p_signal == 0:
        return signal.copy()
    p_noise = p_signal / (10 ** (snr_db / 10.0))
    sigma = np.sqrt(p_noise)
    noise = np.random.normal(0.0, sigma, len(signal))
    return signal + noise


def generate_impulse(length: int, delay: int = 0) -> np.ndarray:
    """
    Genera un impulso unitario (delta de Dirac discreta).
    """
    if delay < 0 or delay >= length:
        raise ValueError("delay must satisfy 0 <= delay < length")
    y = np.zeros(length, dtype=float)
    y[delay] = 1.0
    return y
