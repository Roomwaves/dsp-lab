import numpy as np
import scipy.signal

# --- Issue #1: moving_average ---

def moving_average(signal: np.ndarray, M: int, passes: int = 1) -> np.ndarray:
    """
    Filtro de media móvil causal.
    Implementar el filtro de media móvil con soporte para 1, 2 y 3 pasadas consecutivas.
    """
    if M < 1:
        raise ValueError("M must be >= 1")
    y = signal.copy()
    h = np.ones(M) / M
    for _ in range(passes):
        y = np.convolve(y, h, mode='full')[:len(y)]
    return y

class MovingAverageFilter:
    """
    Filtro de media móvil causal con soporte para procesamiento por bloques y
    múltiples pasadas.
    
    CORRECCIÓN DSP:
    1. Se añadió el parámetro 'passes' en __init__ para corregir el error de
       estado en cascada, evitando el valor hardcodeado passes=1.
    2. Si passes > 1, cada pasada consecutiva del filtro requiere su propio
       historial de estados (retraso acumulado). Se reimplementó el
       procesamiento de bloques utilizando `scipy.signal.lfilter` manteniendo
       de manera consecutiva los vectores de condición inicial y final (zi y zf)
       para cada pasada. De esta manera, el filtrado por bloques produce un
       resultado matemáticamente idéntico a filtrar la señal completa de una
       sola vez.
    """
    def __init__(self, M: int, passes: int = 1) -> None:
        if M < 1:
            raise ValueError("M must be >= 1")
        if passes < 1:
            raise ValueError("passes must be >= 1")
        self.M = M
        self.passes = passes
        self.reset()

    def reset(self) -> None:
        # Inicializamos condiciones iniciales (zi) de tamaño M-1 en cero
        self.states = [
            np.zeros(self.M - 1, dtype=float)
            for _ in range(self.passes)
        ]

    def process_block(self, block: np.ndarray) -> np.ndarray:
        # Los coeficientes del filtro de media móvil para una etapa
        b = np.ones(self.M) / self.M
        a = np.array([1.0])
        current_signal = block.astype(float)
        # Aplicamos lfilter secuencialmente para cada pasada
        for k in range(self.passes):
            current_signal, zf = scipy.signal.lfilter(
                b, a, current_signal, zi=self.states[k]
            )
            self.states[k] = zf
        return current_signal


# --- Issue #2: comb_filter ---

def comb_filter(signal: np.ndarray, b0: float, b1: float, b2: float) -> np.ndarray:
    """
    Filtro peine (comb filter) causal:
    y[n] = b0*x[n] + b1*x[n-1] + b2*x[n-2]
    """
    b = np.array([b0, b1, b2])
    a = np.array([1.0])
    return scipy.signal.lfilter(b, a, signal)

class CombFilterState:
    def __init__(self, b0: float, b1: float, b2: float) -> None:
        self.b0 = b0
        self.b1 = b1
        self.b2 = b2
        self.reset()

    def reset(self) -> None:
        self.x1 = 0.0
        self.x2 = 0.0

    def process_block(self, block: np.ndarray) -> np.ndarray:
        y = np.zeros_like(block)
        for i, val in enumerate(block):
            y[i] = self.b0 * val + self.b1 * self.x1 + self.b2 * self.x2
            self.x2 = self.x1
            self.x1 = val
        return y

# Alias de compatibilidad
CombFilter = CombFilterState


# --- Issue #3: FIR ---

def apply_fir(signal: np.ndarray, coefficients: np.ndarray) -> np.ndarray:
    """
    Aplica un filtro FIR causal con coeficientes arbitrarios.
    """
    return np.convolve(signal, coefficients, mode='full')[:len(signal)]

def truncate_fir(coefficients: np.ndarray, N: int) -> np.ndarray:
    """
    Trunca los coeficientes de un filtro FIR.
    """
    if N < 1 or N > len(coefficients):
        raise ValueError("N must satisfy 1 <= N <= len(coefficients)")
    return coefficients[:N].copy()

class FIRFilter:
    def __init__(self, coefficients: np.ndarray) -> None:
        self.coefficients = coefficients.copy()
        self.M = len(coefficients)
        self.reset()

    def reset(self) -> None:
        self.state = np.zeros(self.M - 1, dtype=float)

    def process_block(self, block: np.ndarray) -> np.ndarray:
        x_padded = np.concatenate([self.state, block])
        y_padded = apply_fir(x_padded, self.coefficients)
        y = y_padded[self.M - 1:]
        if len(block) >= self.M - 1:
            self.state = block[-(self.M - 1):].copy()
        else:
            self.state = np.concatenate([self.state[len(block):], block])
        return y
