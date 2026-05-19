import numpy as np

def moving_average(signal: np.ndarray, M: int, passes: int = 1) -> np.ndarray:
    """
    Filtro de media móvil.
    Implementar el filtro de media móvil con soporte para 1, 2 y 3 pasadas consecutivas.
    """
    raise NotImplementedError("Implementar en Issue #1")

def comb_filter(signal: np.ndarray, b0: float, b1: float, b2: float) -> np.ndarray:
    """
    Filtro peine (comb filter).
    Definido mediante tres coeficientes y dos muestras de retardo.
    """
    raise NotImplementedError("Implementar en Issue #2")

def apply_fir(signal: np.ndarray, coefficients: np.ndarray) -> np.ndarray:
    """
    Aplica un filtro FIR con coeficientes arbitrarios.
    """
    raise NotImplementedError("Implementar en Issue #3")

def truncate_fir(coefficients: np.ndarray, N: int) -> np.ndarray:
    """
    Trunca los coeficientes de un filtro FIR.
    """
    raise NotImplementedError("Implementar en Issue #3")
