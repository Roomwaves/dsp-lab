
# --- Tests para Issue #4: generate_pure_tones ---

def test_tones_output_length():
    """len(output) == int(fs * duration)"""
    pass

def test_tones_single_frequency():
    """Un tono puro a 440 Hz tiene su pico de FFT en 440 Hz."""
    pass

def test_tones_amplitude_scaling():
    """Duplicar amplitud duplica la amplitud de la señal."""
    pass

def test_tones_zero_amplitude():
    """Amplitud 0 produce señal nula."""
    pass

# --- Tests para Issue #4: add_white_noise ---

def test_noise_snr_approximate():
    """La SNR medida empíricamente está dentro de ±2 dB de la pedida."""
    pass

def test_noise_output_length():
    """La longitud de salida es igual a la de entrada."""
    pass

def test_noise_different_each_call():
    """Dos llamadas seguidas producen resultados distintos (aleatoriedad real)."""
    pass
