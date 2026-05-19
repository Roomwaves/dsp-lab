import pytest
import matplotlib
import matplotlib.pyplot as plt
from core.dsp.plots import plot_signal, plot_spectrum, plot_frequency_response, plot_coherence

# Configuramos matplotlib para que no intente abrir ventanas durante los tests
matplotlib.use('Agg')

# --- Tests para Issue #10: Plots ---

def test_plot_signal_returns_figure():
    """La función retorna un objeto matplotlib.figure.Figure."""
    pass

def test_plot_spectrum_returns_figure():
    """La función retorna un objeto matplotlib.figure.Figure."""
    pass

def test_plot_freq_response_has_two_axes():
    """La figura retornada tiene exactamente 2 subplots."""
    pass

def test_plot_coherence_ylim():
    """El eje Y de coherencia tiene límites [0, 1]."""
    pass

def test_plot_signal_xlabel():
    """El eje X tiene label 'Time (s)' o 'Tiempo (s)'."""
    pass

def test_plot_spectrum_db_mode():
    """En modo dB, los valores del eje Y son negativos para magnitudes < 1."""
    pass
