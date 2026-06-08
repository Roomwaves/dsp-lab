import numpy as np
import pytest

from core.dsp.signals import add_white_noise, generate_impulse, generate_pure_tones, generate_square_wave, generate_triangle_wave, generate_white_noise, generate_pink_noise, generate_sweep


class TestGeneratePureTones:
    def test_output_length(self):
        fs = 1000
        duration = 2.5
        signal = generate_pure_tones([100], [1.0], fs, duration)
        assert len(signal) == int(fs * duration)

    def test_single_frequency_peak(self):
        fs = 4000
        duration = 1.0
        freq = 440.0
        signal = generate_pure_tones([freq], [1.0], fs, duration)
        # Use np.fft.rfft for simple checking
        fft_vals = np.abs(np.fft.rfft(signal))
        fft_freqs = np.fft.rfftfreq(len(signal), 1/fs)
        peak_freq = fft_freqs[np.argmax(fft_vals)]
        assert np.abs(peak_freq - freq) < 5.0

    def test_amplitude_scaling(self):
        fs = 1000
        duration = 1.0
        s1 = generate_pure_tones([100], [1.0], fs, duration)
        s2 = generate_pure_tones([100], [2.0], fs, duration)
        np.testing.assert_allclose(s2, s1 * 2.0, rtol=1e-5)

    def test_zero_amplitude(self):
        fs = 1000
        duration = 1.0
        signal = generate_pure_tones([100, 200], [0.0, 0.0], fs, duration)
        np.testing.assert_allclose(signal, 0.0, atol=1e-7)

    def test_multiple_frequencies(self):
        fs = 4000
        duration = 1.0
        signal = generate_pure_tones([200.0, 600.0], [1.0, 0.5], fs, duration)
        fft_vals = np.abs(np.fft.rfft(signal))
        fft_freqs = np.fft.rfftfreq(len(signal), 1/fs)
        
        idx_200 = np.argmin(np.abs(fft_freqs - 200.0))
        idx_600 = np.argmin(np.abs(fft_freqs - 600.0))
        assert fft_vals[idx_200] > np.mean(fft_vals)
        assert fft_vals[idx_600] > np.mean(fft_vals)

    def test_mismatched_lengths_raises(self):
        with pytest.raises(ValueError):
            generate_pure_tones([100, 200], [1.0], 1000, 1.0)


class TestAddWhiteNoise:
    def test_output_length(self):
        x = np.random.randn(100)
        y = add_white_noise(x, 10.0)
        assert len(y) == len(x)

    def test_snr_approximate(self):
        fs = 10000
        t = np.arange(10000) / fs
        clean = np.sin(2 * np.pi * 50 * t)
        
        snr_db = 15.0
        noisy = add_white_noise(clean, snr_db)
        
        noise = noisy - clean
        p_signal = np.mean(clean ** 2)
        p_noise = np.mean(noise ** 2)
        measured_snr_db = 10 * np.log10(p_signal / p_noise)
        
        assert np.abs(measured_snr_db - snr_db) < 3.0

    def test_high_snr_barely_changes_signal(self):
        x = np.sin(np.linspace(0, 10, 1000))
        y = add_white_noise(x, 60.0)
        np.testing.assert_allclose(y, x, atol=0.01)

    def test_randomness_between_calls(self):
        x = np.ones(1000)
        y1 = add_white_noise(x, 10.0)
        y2 = add_white_noise(x, 10.0)
        assert not np.array_equal(y1, y2)

    def test_does_not_modify_input(self):
        x = np.random.randn(100)
        x_orig = x.copy()
        _ = add_white_noise(x, 10.0)
        np.testing.assert_array_equal(x, x_orig)


class TestGenerateImpulse:
    def test_output_length(self):
        for length in [100, 256, 512]:
            assert len(generate_impulse(length)) == length

    def test_single_one_at_zero(self):
        y = generate_impulse(100)
        assert y[0] == 1.0
        assert np.sum(y[1:]) == 0.0

    def test_single_one_at_delay(self):
        y = generate_impulse(100, delay=5)
        assert y[5] == 1.0
        assert np.sum(y[:5]) == 0.0
        assert np.sum(y[6:]) == 0.0

    def test_sum_is_one(self):
        for delay in [0, 10, 49]:
            y = generate_impulse(50, delay=delay)
            assert np.sum(y) == 1.0

    def test_invalid_delay_raises(self):
        with pytest.raises(ValueError):
            generate_impulse(50, delay=50)
        with pytest.raises(ValueError):
            generate_impulse(50, delay=-1)


class TestGenerateSquareWave:
    def test_square_wave_shape(self):
        fs = 1000
        duration = 1.0
        freq = 10.0
        signal = generate_square_wave(freq, 2.0, fs, duration)
        assert len(signal) == int(fs * duration)
        # Check that values are +2.0 or -2.0 (with tolerance)
        assert np.all(np.abs(np.abs(signal) - 2.0) < 1e-9)
        # Check duty cycle (should be 50% positive/negative)
        num_positive = np.sum(signal > 0)
        assert np.abs(num_positive - 500) <= 5

class TestGenerateTriangleWave:
    def test_triangle_wave_shape(self):
        fs = 1000
        duration = 1.0
        freq = 5.0
        signal = generate_triangle_wave(freq, 1.5, fs, duration)
        assert len(signal) == int(fs * duration)
        assert np.max(signal) <= 1.5
        assert np.min(signal) >= -1.5

class TestGenerateWhiteNoise:
    def test_white_noise_bounds(self):
        fs = 10000
        duration = 1.0
        amp = 1.0
        signal = generate_white_noise(amp, fs, duration, gaussian=False)
        assert len(signal) == int(fs * duration)
        assert np.max(signal) <= amp
        assert np.min(signal) >= -amp

    def test_gaussian_noise(self):
        fs = 10000
        duration = 1.0
        amp = 1.5
        signal = generate_white_noise(amp, fs, duration, gaussian=True)
        assert len(signal) == int(fs * duration)
        # In Gaussian noise, standard deviation should match amp (rms)
        std_val = np.std(signal)
        assert np.abs(std_val - amp) < 0.1

class TestGeneratePinkNoise:
    def test_pink_noise_peak(self):
        fs = 8000
        duration = 1.5
        amp = 0.8
        signal = generate_pink_noise(amp, fs, duration)
        assert len(signal) == int(fs * duration)
        # Pink noise should be normalized to peak
        assert np.abs(np.max(np.abs(signal)) - amp) < 1e-5

class TestGenerateSweep:
    def test_linear_sweep(self):
        fs = 8000
        duration = 2.0
        signal = generate_sweep(100.0, 1000.0, "linear", 1.0, fs, duration)
        assert len(signal) == int(fs * duration)
        assert np.max(np.abs(signal)) <= 1.0

    def test_logarithmic_sweep(self):
        fs = 8000
        duration = 2.0
        signal = generate_sweep(20.0, 4000.0, "logarithmic", 1.0, fs, duration)
        assert len(signal) == int(fs * duration)
        assert np.max(np.abs(signal)) <= 1.0

    def test_invalid_log_sweep_raises(self):
        with pytest.raises(ValueError):
            generate_sweep(-10.0, 1000.0, "logarithmic", 1.0, 8000, 1.0)
        with pytest.raises(ValueError):
            generate_sweep(100.0, -1000.0, "logarithmic", 1.0, 8000, 1.0)
