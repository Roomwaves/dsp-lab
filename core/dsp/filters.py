import numpy as np


# --- Issue #1: moving_average ---

def moving_average(signal: np.ndarray, M: int, passes: int = 1) -> np.ndarray:
    """
    Filtro de media móvil.
    Implementar el filtro de media móvil con soporte para 1, 2 y 3 pasadas consecutivas.
    """
    raise NotImplementedError("Implementar en Issue #1")

class MovingAverageFilter:
    def __init__(self, M: int) -> None:
        raise NotImplementedError("Implementar en Issue #1")

    def process_block(self, block: np.ndarray) -> np.ndarray:
        raise NotImplementedError("Implementar en Issue #1")

    def reset(self) -> None:
        raise NotImplementedError("Implementar en Issue #1")


# --- Issue #2: comb_filter ---

def comb_filter(signal: np.ndarray, b0: float, b1: float, b2: float) -> np.ndarray:
    """
    Filtro peine (comb filter).
    Definido mediante tres coeficientes y dos muestras de retardo.
    """
    raise NotImplementedError("Implementar en Issue #2")

class CombFilterState:
    def __init__(self, b0: float, b1: float, b2: float) -> None:
        raise NotImplementedError("Implementar en Issue #2")

    def process_block(self, block: np.ndarray) -> np.ndarray:
        raise NotImplementedError("Implementar en Issue #2")

    def reset(self) -> None:
        raise NotImplementedError("Implementar en Issue #2")

# Alias de compatibilidad
CombFilter = CombFilterState


# --- Issue #3: FIR ---

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

class FIRFilter:
    def __init__(self, coefficients: np.ndarray) -> None:
        raise NotImplementedError("Implementar en Issue #3")

    def process_block(self, block: np.ndarray) -> np.ndarray:
        raise NotImplementedError("Implementar en Issue #3")

    def reset(self) -> None:
        raise NotImplementedError("Implementar en Issue #3")
