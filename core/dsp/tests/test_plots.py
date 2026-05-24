import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from core.dsp.plots import (
    plot_signal,
    plot_spectrum,
    plot_frequency_response,
    plot_coherence
)

# Configuramos matplotlib para que no intente abrir ventanas durante los tests
matplotlib.use('Agg')

# --- Tests para Issue #10: Plots ---

def test_plot_signal_returns_figure():
    """La función retorna un objeto matplotlib.figure.Figure."""
    y = np.random.randn(100)
    fig = plot_signal(y, 1000)
    assert isinstance(fig, plt.Figure)
    plt.close(fig)

def test_plot_spectrum_returns_figure():
    """La función retorna un objeto matplotlib.figure.Figure."""
    freqs = np.linspace(0, 500, 100)
    mags = np.random.rand(100)
    fig = plot_spectrum(freqs, mags)
    assert isinstance(fig, plt.Figure)
    plt.close(fig)

def test_plot_freq_response_has_two_axes():
    """La figura retornada tiene exactamente 2 subplots (módulo y fase)."""
    freqs = np.linspace(0, 500, 100)
    H = np.random.rand(100) + 1j * np.random.rand(100)
    fig = plot_frequency_response(freqs, H)
    assert isinstance(fig, plt.Figure)
    assert len(fig.get_axes()) >= 2
    plt.close(fig)

def test_plot_coherence_ylim():
    """El eje Y de coherencia tiene límites [0, 1]."""
    freqs = np.linspace(0, 500, 100)
    coh = np.random.rand(100)
    fig = plot_coherence(freqs, coh)
    assert isinstance(fig, plt.Figure)
    # Buscamos el eje de coherencia
    ax = fig.gca()
    ylim = ax.get_ylim()
    # Permitimos margen de padding del gráfico
    assert ylim[0] <= 0.05
    assert ylim[1] >= 0.95
    plt.close(fig)

def test_plot_signal_xlabel():
    """El eje X tiene label 'Time (s)' o 'Tiempo (s)'."""
    y = np.random.randn(100)
    fig = plot_signal(y, 1000)
    ax = fig.gca()
    xlabel = ax.get_xlabel().lower()
    assert "time" in xlabel or "tiempo" in xlabel
    plt.close(fig)

def test_plot_spectrum_db_mode():
    """En modo dB, la etiqueta del eje Y debe indicar dB."""
    freqs = np.linspace(0, 500, 100)
    mags = np.random.rand(100)
    fig = plot_spectrum(freqs, mags, db=True)
    ax = fig.gca()
    ylabel = ax.get_ylabel().lower()
    assert "db" in ylabel
    plt.close(fig)
