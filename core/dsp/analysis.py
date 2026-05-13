import numpy as np
import matplotlib.pyplot as plt

def compute_fft(signal: np.ndarray, fs: float) -> tuple[np.ndarray, np.ndarray]:
    """Compute the FFT of a signal.
    
    Args:
        signal: Input signal array
        fs: Sampling frequency
    """
    raise NotImplementedError

def compute_frequency_response(x: np.ndarray, y: np.ndarray, fs: float) -> tuple[np.ndarray, np.ndarray]:
    """Compute the frequency response.
    
    Args:
        x: Input signal
        y: Output signal
        fs: Sampling frequency
    """
    raise NotImplementedError

def plot_spectrum(frequencies: np.ndarray, magnitudes: np.ndarray) -> None:
    """Plot the spectrum.
    
    Args:
        frequencies: Frequency array
        magnitudes: Magnitude array
    """
    plt.plot(frequencies, magnitudes)
    plt.show()