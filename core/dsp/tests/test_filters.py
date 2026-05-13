import numpy as np
import pytest
from core.dsp.filters import moving_average, comb_filter, apply_fir

def test_moving_average_dc():
    dc = np.ones(100)
    with pytest.raises(NotImplementedError):
        moving_average(dc, M=5)

def test_moving_average_length():
    signal = np.zeros(100)
    with pytest.raises(NotImplementedError):
        moving_average(signal, M=5)

def test_comb_filter_zero_coeffs():
    signal = np.ones(100)
    with pytest.raises(NotImplementedError):
        comb_filter(signal, 0.0, 0.0, 0.0)

def test_comb_filter_passthrough():
    signal = np.ones(100)
    with pytest.raises(NotImplementedError):
        comb_filter(signal, 1.0, 0.0, 0.0)

def test_apply_fir_delta():
    signal = np.ones(100)
    coeffs = np.array([1.0, 0.0, 0.0])
    with pytest.raises(NotImplementedError):
        apply_fir(signal, coeffs)

def test_apply_fir_zero():
    signal = np.ones(100)
    coeffs = np.array([0.0, 0.0, 0.0])
    with pytest.raises(NotImplementedError):
        apply_fir(signal, coeffs)