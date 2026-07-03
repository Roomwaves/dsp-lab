# faculty/preentrega/functions.py
# Academic Submission File — re-exports and wraps functions from core/dsp.
# DO NOT duplicate core implementations here.

import os

import matplotlib.pyplot as plt
import numpy as np
from core.dsp.analysis import (
    compute_fft,
    compute_frequency_response,
    convolve_frequency,
    convolve_time,
)

# 1. Imports and re-exports from core/dsp
from core.dsp.coherence import compute_coherence
from core.dsp.filters import apply_fir, comb_filter, moving_average, truncate_fir
from core.dsp.io import load_audio, load_fir_coefficients
from core.dsp.plots import (
    plot_coherence,
    plot_frequency_response,
    plot_signal,
    plot_spectrum,
)
from core.dsp.signals import add_white_noise, generate_impulse, generate_pure_tones

# 2. Compatibility wrappers for the team's notebook

def graficar_temp(t, data, mismo_eje=True):
    """
    Grafica señales temporales usando argumentos variables.
    """
    cant = len(data)
    if mismo_eje:
        for i, datos in enumerate(data):
            plt.plot(t, datos, label=f'Señal {i+1}')
        plt.title('Señales Temporales')
        plt.xlabel('Tiempo [segundos]')
        plt.ylabel('Amplitud')
        plt.grid(True)
        plt.legend()
        plt.show()
    else: 
        fig, axes = plt.subplots(cant, 1, sharex=True, figsize=(8, 2*cant))
        if cant == 1:
            axes = [axes]

        for i, datos in enumerate(data):
            axes[i].plot(t, datos, color=f'C{i}')
            axes[i].set_title(f'Señal {i+1}')
            axes[i].set_ylabel('Amplitud')
            axes[i].grid(True)

        plt.xlabel('Tiempo [segundos]')
        plt.tight_layout()
        plt.show()

def graficar_frecuencias(t, data, fs, mismo_eje=True):
    """
    Grafica la magnitud del espectro de frecuencia.
    """
    cant = len(data)
    n = len(t)
    freq = np.fft.rfftfreq(n, d=1/fs)
    espectros = [np.abs(np.fft.rfft(señal)) for señal in data]

    if mismo_eje:
        for i, magnitud in enumerate(espectros):
            plt.plot(freq, magnitud, label=f'Señal {i+1}')
        plt.title('Espectro de Amplitud (Dominio de la Frecuencia)')
        plt.xlabel('Frecuencia [Hz]')
        plt.ylabel('Magnitud')
        plt.grid(True)
        plt.legend()
        plt.show()
    else: 
        fig, axes = plt.subplots(cant, 1, sharex=True, figsize=(8, 2*cant))
        if cant == 1: 
            axes = [axes]

        for i, magnitud in enumerate(espectros):
            axes[i].plot(freq, magnitud, color=f'C{i}')
            axes[i].set_title(f'Espectro Señal {i+1}')
            axes[i].set_ylabel('Magnitud')
            axes[i].grid(True)

        plt.xlabel('Frecuencia [Hz]')
        plt.tight_layout()
        plt.show()

def rta_frecuencia(x, y):
    """Calcula la respuesta en frecuencia de un sistema dado su entrada y salida."""
    freqs, H = compute_frequency_response(x, y, fs=44100)
    return H

def identificar_sistema(x, y, fs=44100, window_size=1024):
    """
    Calcula la respuesta en frecuencia estimador H1 = Gxy / Gxx
    utilizando promediado Welch para suavizar el ruido.
    """
    freqs, H = compute_frequency_response(x, y, fs=fs, window_size=window_size)
    return freqs, H

def evaluar_coherencia(x, y, fs=44100, window_size=1024):
    """
    Calcula la coherencia cuadrática gamma_xy^2(w) = |Gxy|^2 / (Gxx * Gyy)
    para analizar la linealidad entre la entrada x y la salida y.
    """
    freqs, coh = compute_coherence(x, y, fs=fs, window_size=window_size)
    return freqs, coh

def suma_tonos_puros(f, a, duracion, amp_ruido, fs=44100):
    """Suma tonos puros con ruido blanco de distintas amplitudes."""
    signal = generate_pure_tones(frequencies=list(f), amplitudes=list(a), fs=fs, duration=duracion)
    ruido = amp_ruido * np.random.normal(0, 1, len(signal))
    return signal + ruido

def suma_musical(wav, amp_ruido):
    """Suma señal musical con ruido blanco adaptándose a canales mono o estéreo."""
    # Limpiar ruta para compatibilidad de SO
    wav_clean = wav.replace("\\", "/")
    if not os.path.isabs(wav_clean):
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        if wav_clean.startswith("archivos/"):
            filepath = os.path.join(project_root, wav_clean)
        else:
            filepath = os.path.join(project_root, "archivos", wav_clean)
    else:
        filepath = wav_clean

    signal, fs = load_audio(filepath)
    ruido = amp_ruido * np.random.normal(0, 1, signal.shape)
    return signal + ruido

def filtro_media_movil(x, m, p):
    """Aplica un filtro de promedio móvil de longitud m a una señal x."""
    y = moving_average(x, M=m, passes=p)
    h = np.ones(m) / m
    return y, h

def filtro_peine(x, a, b, c):
    """Aplica un filtro peine a una señal x respetando la ecuación del profesor."""
    y = comb_filter(x, b0=a, b1=b, b2=c)
    h = np.array([a, b, c])
    return y, h

def filtro_fir(x):
    """Aplica un filtro FIR a una señal x usando coeficientes predefinidos."""
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    coefficients_path = os.path.join(project_root, "archivos", "fir_hamming_1000Hz.npy")
    h = load_fir_coefficients(coefficients_path)
    y = apply_fir(x, h)
    return y, h

def filtrar_frecuencia_manual(x, b):
    """Realiza la convolución circular en frecuencia recortada a la longitud de entrada."""
    return convolve_frequency(x, b)[:len(x)]


__all__ = [
    "compute_fft",
    "compute_frequency_response",
    "compute_coherence",
    "convolve_frequency",
    "convolve_time",
    "apply_fir",
    "truncate_fir",
    "comb_filter",
    "moving_average",
    "load_audio",
    "load_fir_coefficients",
    "add_white_noise",
    "generate_impulse",
    "generate_pure_tones",
    "plot_signal",
    "plot_spectrum",
    "plot_frequency_response",
    "plot_coherence",
    "identificar_sistema",
    "evaluar_coherencia",
    "graficar_temp",
    "graficar_frecuencias",
    "rta_frecuencia",
    "suma_tonos_puros",
    "suma_musical",
    "filtro_media_movil",
    "filtro_peine",
    "filtro_fir",
    "filtrar_frecuencia_manual",
]


# --- Tests Locales (Solo se ejecutan si se corre el archivo directamente) ---

if __name__ == "__main__":
    print("Corriendo pruebas locales en functions.py...")
    fs = 44100
    duracion = 2.0
    t_vector = np.arange(0, duracion, 1/fs)

    f_tonos = [500, 1000, 5000]
    a_tonos = [1.0, 0.5, 0.2]
    x_tonos = suma_tonos_puros(f_tonos, a_tonos, duracion, amp_ruido=0.05)
    x_musical = suma_musical('musica_ruido_0.01.wav', amp_ruido=0.02)

    y_tonos_media, h_media = filtro_media_movil(x_tonos, m=20, p=2)
    y_tonos_peine, h_peine = filtro_peine(x_tonos, a=0.1, b=0.5, c=0.4)
    y_tonos_fir, h_fir = filtro_fir(x_tonos)

    print("Prueba completada exitosamente.")