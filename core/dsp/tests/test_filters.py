import numpy as np
import pytest
from core.dsp.filters import (
    moving_average,
    MovingAverageFilter,
    comb_filter,
    CombFilter,
    apply_fir,
    truncate_fir
)

# --- Tests para Issue #1: moving_average ---

def test_moving_average_dc_preservation():
    """Una señal constante filtrada debe seguir siendo constante."""
    x = np.ones(100)
    y = moving_average(x, M=5)
    # The transient part is first M-1 samples, after that it must be exactly 1.0
    np.testing.assert_allclose(y[4:], 1.0)

def test_moving_average_output_length():
    """La longitud de la salida debe ser igual a la de la entrada."""
    x = np.random.randn(50)
    y = moving_average(x, M=5)
    assert len(y) == len(x)

def test_moving_average_passes_smoothness():
    """La señal con 2 pasadas debe tener menor varianza que con 1 pasada sobre señal ruidosa."""
    x = np.random.randn(1000)
    y1 = moving_average(x, M=10, passes=1)
    y2 = moving_average(x, M=10, passes=2)
    assert np.var(y2) < np.var(y1)

def test_moving_average_m1_identity():
    """Con M=1 la salida debe ser idéntica a la entrada."""
    x = np.random.randn(50)
    y = moving_average(x, M=1)
    np.testing.assert_allclose(y, x)

def test_moving_average_known_output():
    """Para una señal corta conocida y M=3, verificar valores exactos de salida."""
    x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    y = moving_average(x, M=3, passes=1)
    expected = np.array([1/3, 1.0, 2.0, 3.0, 4.0])
    np.testing.assert_allclose(y, expected)

def test_moving_average_filter_stateful():
    """Verificar que la versión stateful (MovingAverageFilter) se comporta igual bloque a bloque."""
    x = np.random.randn(100)
    ma_class = MovingAverageFilter(M=4)
    # Process in two blocks
    out1 = ma_class.process_block(x[:50])
    out2 = ma_class.process_block(x[50:])
    out_stateful = np.concatenate([out1, out2])
    
    # Non-stateful equivalent
    out_functional = moving_average(x, M=4, passes=1)
    np.testing.assert_allclose(out_stateful, out_functional)


# --- Tests para Issue #2: comb_filter ---

def test_comb_zero_coefficients():
    """Con coeficientes nulos, salida de ceros."""
    x = np.random.randn(50)
    y = comb_filter(x, 0.0, 0.0, 0.0)
    np.testing.assert_allclose(y, 0.0)

def test_comb_identity():
    """Con b0=1, b1=0, b2=0, salida igual a entrada."""
    x = np.random.randn(50)
    y = comb_filter(x, 1.0, 0.0, 0.0)
    np.testing.assert_allclose(y, x)

def test_comb_output_length():
    """Longitud de salida igual a entrada."""
    x = np.random.randn(50)
    y = comb_filter(x, 0.5, 0.2, 0.1)
    assert len(y) == len(x)

def test_comb_known_output():
    """Para impulso, salida debe ser [b0, b1, b2, 0, 0, ...]."""
    x = np.array([1.0, 0.0, 0.0, 0.0, 0.0])
    b0, b1, b2 = 0.5, -0.3, 0.1
    y = comb_filter(x, b0, b1, b2)
    expected = np.array([b0, b1, b2, 0.0, 0.0])
    np.testing.assert_allclose(y, expected)

def test_comb_delay_two():
    """Con b0=0, b1=0, b2=1, salida es entrada retardada 2 muestras."""
    x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    y = comb_filter(x, 0.0, 0.0, 1.0)
    expected = np.array([0.0, 0.0, 1.0, 2.0, 3.0])
    np.testing.assert_allclose(y, expected)

def test_comb_filter_stateful():
    """Verificar que la versión stateful (CombFilter) se comporta igual bloque a bloque."""
    x = np.random.randn(100)
    b0, b1, b2 = 0.5, 0.3, -0.2
    cf = CombFilter(b0, b1, b2)
    out1 = cf.process_block(x[:50])
    out2 = cf.process_block(x[50:])
    out_stateful = np.concatenate([out1, out2])
    
    out_functional = comb_filter(x, b0, b1, b2)
    np.testing.assert_allclose(out_stateful, out_functional)


# --- Tests para Issue #3: FIR ---

def test_fir_delta_identity():
    """Con coefficients=[1.0], salida igual a entrada."""
    x = np.random.randn(50)
    y = apply_fir(x, np.array([1.0]))
    np.testing.assert_allclose(y, x)

def test_fir_output_length():
    """Longitud de salida igual a entrada."""
    x = np.random.randn(50)
    y = apply_fir(x, np.array([0.1, 0.2, 0.3]))
    assert len(y) == len(x)

def test_fir_moving_avg_equivalence():
    """FIR con coef [1/3, 1/3, 1/3] equivalente a moving_average(M=3)."""
    x = np.random.randn(100)
    coefs = np.array([1/3, 1/3, 1/3])
    y_fir = apply_fir(x, coefs)
    y_ma = moving_average(x, M=3)
    np.testing.assert_allclose(y_fir, y_ma)

def test_truncate_length():
    """len(truncate_fir(h, N)) == N."""
    h = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    assert len(truncate_fir(h, 3)) == 3

def test_truncate_values():
    """Valores truncados son los primeros N del original."""
    h = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    np.testing.assert_allclose(truncate_fir(h, 3), np.array([1.0, 2.0, 3.0]))

def test_truncate_full():
    """Truncar con N=len(h) devuelve arreglo completo."""
    h = np.array([1.0, 2.0, 3.0])
    np.testing.assert_allclose(truncate_fir(h, 3), h)
    np.testing.assert_allclose(truncate_fir(h, 5), h)
