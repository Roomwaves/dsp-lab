import numpy as np

def compute_coherence(x: np.ndarray, y: np.ndarray, fs: float) -> tuple[np.ndarray, np.ndarray]:
    """Compute the coherence between two signals.
    
    γ²xy(ω) = |Gxy(ω)|² / (Gxx(ω)·Gyy(ω))
    
    Args:
        x: First signal
        y: Second signal
        fs: Sampling frequency
    """
    raise NotImplementedError