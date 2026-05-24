import numpy as np
import pytest
from core.dsp.coherence import compute_psd, compute_cpsd, compute_coherence

class TestPSDAndCPSD:
    def test_psd_real_positive(self):
        fs = 1000
        x = np.random.randn(1000)
        freqs, Gxx = compute_psd(x, fs)
        assert np.all(np.isreal(Gxx))
        assert np.all(Gxx >= 0.0)

    def test_psd_frequency_range(self):
        fs = 1000
        x = np.random.randn(1000)
        freqs, Gxx = compute_psd(x, fs)
        assert freqs[0] == 0.0
        assert freqs[-1] <= fs / 2.0

    def test_psd_lengths_match(self):
        fs = 1000
        x = np.random.randn(1000)
        freqs, Gxx = compute_psd(x, fs)
        assert len(freqs) == len(Gxx)

    def test_cpsd_lengths_match(self):
        fs = 1000
        x = np.random.randn(1000)
        y = np.random.randn(1000)
        freqs, Gxy = compute_cpsd(x, y, fs)
        assert len(freqs) == len(Gxy)

    def test_cpsd_same_signal(self):
        fs = 1000
        x = np.random.randn(1000)
        freqs, Gxy = compute_cpsd(x, x, fs)
        freqs, Gxx = compute_psd(x, fs)
        np.testing.assert_allclose(Gxy, Gxx, rtol=1e-5)

    def test_psd_white_noise_flat(self):
        fs = 10000
        x = np.random.randn(50000)
        freqs, Gxx = compute_psd(x, fs, n_segments=32)
        mean_val = np.mean(Gxx)
        assert np.std(Gxx) < mean_val * 0.8


class TestCoherence:
    def test_coherence_range(self):
        fs = 1000
        x = np.random.randn(1000)
        y = np.random.randn(1000)
        freqs, coh = compute_coherence(x, y, fs)
        assert np.all(coh >= -1e-7)
        assert np.all(coh <= 1.0 + 1e-7)

    def test_coherence_identity(self):
        fs = 1000
        x = np.random.randn(1000)
        freqs, coh = compute_coherence(x, x, fs)
        np.testing.assert_allclose(coh, 1.0, rtol=1e-5)

    def test_coherence_independent(self):
        fs = 10000
        x = np.random.randn(20000)
        y = np.random.randn(20000)
        freqs, coh = compute_coherence(x, y, fs, n_segments=32)
        assert np.mean(coh) < 0.3

    def test_coherence_lengths_match(self):
        fs = 1000
        x = np.random.randn(1000)
        y = np.random.randn(1000)
        freqs, coh = compute_coherence(x, y, fs)
        assert len(freqs) == len(coh)

    def test_coherence_real(self):
        fs = 1000
        x = np.random.randn(1000)
        y = np.random.randn(1000)
        freqs, coh = compute_coherence(x, y, fs)
        assert np.all(np.isreal(coh))
