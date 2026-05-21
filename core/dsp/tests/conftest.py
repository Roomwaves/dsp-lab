import numpy as np
import pytest


@pytest.fixture
def white_noise_signal():
    return np.random.randn(44100)

@pytest.fixture
def dc_signal():
    return np.ones(44100)

@pytest.fixture
def sine_440hz():
    t = np.arange(44100) / 44100
    return np.sin(2 * np.pi * 440 * t)