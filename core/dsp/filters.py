import numpy as np
import scipy.signal


def moving_average(signal: np.ndarray, M: int, passes: int = 1) -> np.ndarray:
    """
    Filtro de media móvil.
    Implementar el filtro de media móvil con soporte para 1, 2 y 3 pasadas consecutivas.
    """
    if M < 1:
        raise ValueError(f"M must be >= 1, got {M}")
    if not 1 <= passes <= 3:
        raise ValueError(f"passes must be 1, 2 or 3, got {passes}")
    if len(signal) < M:
        raise ValueError(f"signal length ({len(signal)}) must be >= M ({M})")

    out = signal.astype(float)
    b = np.ones(M) / M
    a = 1.0
    for _ in range(passes):
        out = scipy.signal.lfilter(b, a, out)
    return out

class MovingAverageFilter:
    def __init__(self, M: int) -> None:
        if M < 1:
            raise ValueError(f"M must be >= 1, got {M}")
        self.M = M
        self._buffer = np.zeros(M)
        self._write_index = 0

    def process_block(self, block: np.ndarray) -> np.ndarray:
        out = np.zeros_like(block, dtype=float)
        for i in range(len(block)):
            self._buffer[self._write_index] = block[i]
            self._write_index = (self._write_index + 1) % self.M
            out[i] = np.sum(self._buffer) / self.M
        return out

    def reset(self) -> None:
        self._buffer.fill(0.0)
        self._write_index = 0

def comb_filter(signal: np.ndarray, b0: float, b1: float, b2: float) -> np.ndarray:
    """
    Filtro peine (comb filter).
    Definido mediante tres coeficientes y dos muestras de retardo.
    """
    b = np.array([b0, b1, b2], dtype=float)
    a = 1.0
    return scipy.signal.lfilter(b, a, signal)

class CombFilter:
    def __init__(self, b0: float, b1: float, b2: float) -> None:
        self.b0 = b0
        self.b1 = b1
        self.b2 = b2
        self._buffer = np.zeros(2)

    def process_block(self, block: np.ndarray) -> np.ndarray:
        out = np.zeros_like(block, dtype=float)
        for i in range(len(block)):
            x = block[i]
            out[i] = self.b0 * x + self.b1 * self._buffer[0] + self.b2 * self._buffer[1]
            self._buffer[1] = self._buffer[0]
            self._buffer[0] = x
        return out

    def reset(self) -> None:
        self._buffer.fill(0.0)

def apply_fir(signal: np.ndarray, coefficients: np.ndarray) -> np.ndarray:
    """
    Aplica un filtro FIR con coeficientes arbitrarios.
    """
    return scipy.signal.lfilter(coefficients, 1.0, signal)

def truncate_fir(coefficients: np.ndarray, N: int) -> np.ndarray:
    """
    Trunca los coeficientes de un filtro FIR.
    """
    if N < 1:
        raise ValueError(f"N must be >= 1, got {N}")
    if N > len(coefficients):
        return coefficients.copy()
    return coefficients[:N].copy()

