import numpy as np

from core.dsp.analysis import (
    compute_fft,
    compute_frequency_response,
    compute_magnitude_db,
    compute_phase,
    convolve_frequency,
    convolve_time,
)


class TestComputeFFT:
    def test_lengths_match(self):
        fs = 1000
        x = np.random.randn(100)
        freqs, mags = compute_fft(x, fs)
        assert len(freqs) == len(mags)

    def test_frequency_range(self):
        fs = 1000
        x = np.random.randn(100)
        freqs, mags = compute_fft(x, fs)
        assert freqs[0] == 0.0
        assert freqs[-1] <= fs / 2.0

    def test_magnitudes_non_negative(self):
        fs = 1000
        x = np.random.randn(100)
        freqs, mags = compute_fft(x, fs)
        assert np.all(mags >= 0.0)

    def test_dc_signal_peak_at_zero(self):
        fs = 1000
        x = np.ones(1000)
        freqs, mags = compute_fft(x, fs)
        assert np.argmax(mags) == 0

    def test_sine_peak_frequency(self):
        fs = 4000
        t = np.arange(4000) / fs
        x = np.sin(2 * np.pi * 440 * t)
        freqs, mags = compute_fft(x, fs)
        peak_freq = freqs[np.argmax(mags)]
        assert np.abs(peak_freq - 440.0) < 5.0

    def test_output_types(self):
        fs = 1000
        x = np.random.randn(100)
        freqs, mags = compute_fft(x, fs)
        assert not np.iscomplexobj(freqs)
        assert not np.iscomplexobj(mags)

    def test_nyquist_not_exceeded(self):
        fs = 1000
        x = np.random.randn(100)
        freqs, mags = compute_fft(x, fs)
        assert freqs[-1] <= fs / 2.0


class TestFrequencyResponse:
    def test_freq_response_identity_system(self):
        fs = 1000
        x = np.random.randn(1000)
        freqs, H = compute_frequency_response(x, x, fs)
        np.testing.assert_allclose(np.abs(H), 1.0, rtol=1e-5)

    def test_freq_response_lengths_match(self):
        fs = 1000
        x = np.random.randn(100)
        y = np.random.randn(100)
        freqs, H = compute_frequency_response(x, y, fs)
        assert len(freqs) == len(H)

    def test_freq_response_complex(self):
        fs = 1000
        x = np.random.randn(100)
        y = np.random.randn(100)
        freqs, H = compute_frequency_response(x, y, fs)
        assert np.iscomplexobj(H)

    def test_magnitude_db_units(self):
        H = np.array([1.0, 10.0, 0.1, 0.0])
        mag_db = compute_magnitude_db(H)
        assert np.abs(mag_db[0] - 0.0) < 1e-5
        assert np.abs(mag_db[1] - 20.0) < 1e-5
        assert np.abs(mag_db[2] - (-20.0)) < 1e-5

    def test_phase_range(self):
        H = np.array([1+1j, -1-1j, 1-1j, -1+1j])
        phase = compute_phase(H)
        assert np.all(phase >= -np.pi)
        assert np.all(phase <= np.pi)

    def test_freq_response_frequency_range(self):
        fs = 1000
        x = np.random.randn(100)
        y = np.random.randn(100)
        freqs, H = compute_frequency_response(x, y, fs)
        assert freqs[0] == 0.0
        assert freqs[-1] <= fs / 2.0

    def test_freq_response_numerical_stability(self):
        fs = 1000
        # Entrada cero
        x = np.zeros(100)
        y = np.random.randn(100)
        freqs, H = compute_frequency_response(x, y, fs)
        assert np.all(np.isfinite(H))
        
        # Entrada extremadamente pequeña (ej. 1e-25)
        x_small = np.ones(100) * 1e-25
        y_ones = np.ones(100)
        freqs, H_small = compute_frequency_response(x_small, y_ones, fs)
        assert np.all(np.isfinite(H_small))
        assert np.max(np.abs(H_small)) <= 1e15


class TestConvolveTime:
    def test_output_length(self):
        x = np.random.randn(50)
        h = np.random.randn(10)
        y = convolve_time(x, h)
        assert len(y) == len(x) + len(h) - 1

    def test_delta_h_is_identity(self):
        x = np.random.randn(50)
        h = np.array([1.0])
        y = convolve_time(x, h)
        np.testing.assert_allclose(y, x)

    def test_output_is_ndarray(self):
        x = np.random.randn(50)
        h = np.random.randn(10)
        y = convolve_time(x, h)
        assert isinstance(y, np.ndarray)


class TestConvolveFrequency:
    def test_output_length(self):
        x = np.random.randn(50)
        h = np.random.randn(10)
        y = convolve_frequency(x, h)
        assert len(y) == len(x) + len(h) - 1

    def test_equivalence_with_convolve_time(self):
        x = np.random.randn(100)
        h = np.random.randn(15)
        y1 = convolve_time(x, h)
        y2 = convolve_frequency(x, h)
        np.testing.assert_allclose(y2, y1, atol=1e-8)

    def test_delta_h_is_identity(self):
        x = np.random.randn(50)
        h = np.array([1.0])
        y = convolve_frequency(x, h)
        np.testing.assert_allclose(y, x)

    def test_output_is_real(self):
        x = np.random.randn(100)
        h = np.random.randn(15)
        y = convolve_frequency(x, h)
        assert not np.iscomplexobj(y)

    def test_zero_padding_correctness(self):
        signal = np.array([1.0, 2.0, 3.0])
        h = np.array([1.0, 1.0])
        y = convolve_frequency(signal, h)
        expected = np.array([1.0, 3.0, 5.0, 3.0])
        np.testing.assert_allclose(y, expected, atol=1e-10)
