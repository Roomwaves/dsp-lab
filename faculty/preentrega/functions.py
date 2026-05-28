# This file imports from core/dsp package
"""Generar las siguientes señales temporales:

Suma de tonos puros + ruido blanco de distintas amplitudes.

Señal musical + ruido blanco de distintas amplitudes."""

import matplotlib.pyplot as plt
import numpy as np

def suma_tonos_puros(f, a, n, amp_ruido, fs = 44100):
    """Suma tonos puros con ruido blanco de distintas amplitudes.
    ----
    Parametros:
    f: array de frecuencias
    a: array de amplitudes de cada tono (misma longitud que f)
    n: float - cantidad de muestras
    amp_ruido: float - amplitud del ruido blanco
    fs: int - frecuencia de muestreo, por defecto 44100 Hz
    ----
    Salida:
    señal: array de señal generada"""
    long = len(f)
    t = np.arange(0,n,1/fs)
    tonos = np.zeros(len(t))
    for i in range(long):
        tonos += a[i] * np.sin(2*np.pi*f[i]*t)
    ruido = amp_ruido * np.random.normal(0,1,len(t))
    señal = tonos + ruido
    return señal

f_test = np.array([440, 880, 1320])        # Fundamental, 2do y 3er armónico
a_test = np.array([1.0, 0.5, 0.25])       # Amplitudes en progresión geométrica
n = 500                            # 1 segundo
fs = 44100                                # CD Quality
ruido_amp = 0.05                          # SNR alta (ruido bajo)

señal_a = suma_tonos_puros(f_test, a_test, n, ruido_amp, fs)
print(señal_a)