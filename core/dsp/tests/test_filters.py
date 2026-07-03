import numpy as np
import pytest

from core.dsp.filters import (
    MovingAverageFilter,
    apply_fir,
    comb_filter,
    moving_average,
    truncate_fir,
)


class TestMovingAverage:
    def test_dc_preservation(self):
        x = np.ones(100)
        y = moving_average(x, M=5)
        np.testing.assert_allclose(y[4:], 1.0)

    def test_output_length(self):
        for M in [3, 8, 16, 32]:
            x = np.random.randn(50)
            y = moving_average(x, M=M)
            assert len(y) == len(x)

    def test_m1_is_identity(self):
        x = np.random.randn(50)
        y = moving_average(x, M=1)
        np.testing.assert_allclose(y, x)

    def test_passes_increase_smoothness(self):
        x = np.random.randn(1000)
        y1 = moving_average(x, M=10, passes=1)
        y2 = moving_average(x, M=10, passes=2)
        y3 = moving_average(x, M=10, passes=3)
        assert np.var(y2) < np.var(y1)
        assert np.var(y3) < np.var(y2)

    def test_does_not_modify_input(self):
        x = np.random.randn(50)
        x_orig = x.copy()
        _ = moving_average(x, M=5)
        np.testing.assert_array_equal(x, x_orig)

    def test_reduces_noise(self):
        x = np.random.randn(500)
        y = moving_average(x, M=5)
        assert np.var(np.diff(y)) < np.var(np.diff(x))


class TestMovingAverageFilter:
    def test_block_output_length(self):
        for block_size in [256, 512, 1024]:
            block = np.random.randn(block_size)
            ma = MovingAverageFilter(M=5)
            y = ma.process_block(block)
            assert len(y) == len(block)

    def test_block_consistency_with_batch(self):
        x = np.random.randn(1500)
        ma = MovingAverageFilter(M=5)
        # Process in blocks of 512
        y1 = ma.process_block(x[:512])
        y2 = ma.process_block(x[512:1024])
        y3 = ma.process_block(x[1024:])
        out_stateful = np.concatenate([y1, y2, y3])
        out_batch = moving_average(x, M=5)
        np.testing.assert_allclose(out_stateful[10:-10], out_batch[10:-10])

    def test_multi_pass_block_consistency_with_batch(self):
        x = np.random.randn(1500)
        for passes in [1, 2, 3]:
            ma = MovingAverageFilter(M=5, passes=passes)
            # Process in blocks of 512
            y1 = ma.process_block(x[:512])
            y2 = ma.process_block(x[512:1024])
            y3 = ma.process_block(x[1024:])
            out_stateful = np.concatenate([y1, y2, y3])
            out_batch = moving_average(x, M=5, passes=passes)
            # Con scipy.signal.lfilter con zi/zf, la igualdad matemática
            # debe ser exacta en todo el vector
            np.testing.assert_allclose(out_stateful, out_batch)

    def test_reset_restores_initial_state(self):
        x = np.random.randn(500)
        ma = MovingAverageFilter(M=5)
        y1 = ma.process_block(x)
        ma.reset()
        y2 = ma.process_block(x)
        np.testing.assert_array_equal(y1, y2)

    def test_state_persists_between_blocks(self):
        x = np.ones(1000)
        ma = MovingAverageFilter(M=5)
        y1 = ma.process_block(x[:500])
        y2 = ma.process_block(x[500:])
        out = np.concatenate([y1, y2])
        np.testing.assert_allclose(out[10:], 1.0)


class TestCombFilter:
    def test_zero_coefficients(self):
        x = np.random.randn(50)
        y = comb_filter(x, 0.0, 0.0, 0.0)
        np.testing.assert_allclose(y, 0.0)

    def test_identity_b0_only(self):
        x = np.random.randn(50)
        y = comb_filter(x, 1.0, 0.0, 0.0)
        np.testing.assert_allclose(y, x)

    def test_output_length(self):
        x = np.random.randn(50)
        y = comb_filter(x, 0.5, 0.2, 0.1)
        assert len(y) == len(x)

    def test_impulse_response(self):
        x = np.zeros(50)
        x[0] = 1.0
        b0, b1, b2 = 0.5, -0.3, 0.1
        y = comb_filter(x, b0, b1, b2)
        assert y[0] == b0
        assert y[1] == b1
        assert y[2] == b2
        np.testing.assert_allclose(y[3:], 0.0)

    def test_delay_two(self):
        x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        y = comb_filter(x, 0.0, 0.0, 1.0)
        expected = np.array([0.0, 0.0, 1.0, 2.0, 3.0])
        np.testing.assert_allclose(y, expected)

    def test_does_not_modify_input(self):
        x = np.random.randn(50)
        x_orig = x.copy()
        _ = comb_filter(x, 0.5, 0.2, 0.1)
        np.testing.assert_array_equal(x, x_orig)


class TestApplyFIR:
    def test_delta_coefficients_is_identity(self):
        x = np.random.randn(50)
        y = apply_fir(x, np.array([1.0]))
        np.testing.assert_allclose(y, x)

    def test_output_length(self):
        x = np.random.randn(50)
        y = apply_fir(x, np.array([0.1, 0.2, 0.3]))
        assert len(y) == len(x)

    def test_equivalence_with_moving_average(self):
        x = np.random.randn(100)
        coefs = np.ones(5) / 5
        y_fir = apply_fir(x, coefs)
        y_ma = moving_average(x, M=5)
        np.testing.assert_allclose(y_fir, y_ma)

    def test_does_not_modify_input(self):
        x = np.random.randn(50)
        x_orig = x.copy()
        _ = apply_fir(x, np.array([0.1, 0.2]))
        np.testing.assert_array_equal(x, x_orig)


class TestTruncateFIR:
    def test_output_length(self):
        h = np.random.randn(20)
        for N in [1, 3, 5, 10]:
            assert len(truncate_fir(h, N, mode='symmetric')) == N
            assert len(truncate_fir(h, N, mode='causal')) == N

    def test_values_are_first_n_causal(self):
        h = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        np.testing.assert_allclose(truncate_fir(h, 3, mode='causal'), np.array([1.0, 2.0, 3.0]))

    def test_symmetric_truncation_centered(self):
        # Filtro simétrico con pico en el centro (índice 2)
        h = np.array([0.1, 0.5, 1.0, 0.5, 0.1])
        # Al pedir N=3 en modo simétrico, debe tomar la ventana centrada en 1.0 -> [0.5, 1.0, 0.5]
        h_trunc = truncate_fir(h, 3, mode='symmetric')
        np.testing.assert_allclose(h_trunc, np.array([0.5, 1.0, 0.5]))

    def test_full_length_returns_original(self):
        h = np.array([1.0, 2.0, 3.0])
        np.testing.assert_allclose(truncate_fir(h, 3), h)

    def test_does_not_modify_original(self):
        h = np.array([1.0, 2.0, 3.0])
        h_orig = h.copy()
        _ = truncate_fir(h, 2)
        np.testing.assert_array_equal(h, h_orig)

    def test_invalid_n_raises(self):
        h = np.array([1.0, 2.0, 3.0])
        with pytest.raises((ValueError, IndexError)):
            truncate_fir(h, 0)
        with pytest.raises((ValueError, IndexError)):
            truncate_fir(h, 4)
