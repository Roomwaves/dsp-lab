import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pytest

from core.dsp.plots import (
    plot_coherence,
    plot_frequency_response,
    plot_signal,
    plot_spectrum,
)

# Configuramos matplotlib para que no intente abrir ventanas durante los tests
matplotlib.use('Agg')

class TestPlotSignal:
    def test_no_crash(self):
        y = np.random.randn(100)
        try:
            fig = plot_signal(y, 1000)
            plt.close(fig)
        except Exception as e:
            pytest.fail(f"plot_signal raised exception: {e}")

    def test_returns_figure(self):
        y = np.random.randn(100)
        fig = plot_signal(y, 1000)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)


class TestPlotSpectrum:
    def test_no_crash(self):
        freqs = np.linspace(0, 500, 100)
        mags = np.random.rand(100)
        try:
            fig = plot_spectrum(freqs, mags)
            plt.close(fig)
        except Exception as e:
            pytest.fail(f"plot_spectrum raised exception: {e}")

    def test_returns_figure(self):
        freqs = np.linspace(0, 500, 100)
        mags = np.random.rand(100)
        fig = plot_spectrum(freqs, mags)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_db_mode_no_crash(self):
        freqs = np.linspace(0, 500, 100)
        mags = np.random.rand(100)
        try:
            fig = plot_spectrum(freqs, mags, db=True)
            plt.close(fig)
        except Exception as e:
            pytest.fail(f"plot_spectrum in db mode raised exception: {e}")


class TestPlotFrequencyResponse:
    def test_no_crash(self):
        freqs = np.linspace(0, 500, 100)
        H = np.random.rand(100) + 1j * np.random.rand(100)
        try:
            fig = plot_frequency_response(freqs, H)
            plt.close(fig)
        except Exception as e:
            pytest.fail(f"plot_frequency_response raised exception: {e}")

    def test_returns_figure(self):
        freqs = np.linspace(0, 500, 100)
        H = np.random.rand(100) + 1j * np.random.rand(100)
        fig = plot_frequency_response(freqs, H)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_has_two_axes(self):
        freqs = np.linspace(0, 500, 100)
        H = np.random.rand(100) + 1j * np.random.rand(100)
        fig = plot_frequency_response(freqs, H)
        assert len(fig.get_axes()) >= 2
        plt.close(fig)


class TestPlotCoherence:
    def test_no_crash(self):
        freqs = np.linspace(0, 500, 100)
        coh = np.random.rand(100)
        try:
            fig = plot_coherence(freqs, coh)
            plt.close(fig)
        except Exception as e:
            pytest.fail(f"plot_coherence raised exception: {e}")

    def test_returns_figure(self):
        freqs = np.linspace(0, 500, 100)
        coh = np.random.rand(100)
        fig = plot_coherence(freqs, coh)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)
