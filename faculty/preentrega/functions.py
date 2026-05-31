# This file imports from core/dsp package
import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf
import scipy.signal as scipy

def suma_tonos_puros(f, a, t, amp_ruido, fs = 44100):
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
    t = np.arange(0,len(t),1/fs)
    tonos = np.zeros(len(t))
    for i in range(long):
        tonos += a[i] * np.sin(2*np.pi*f[i]*t)
    ruido = amp_ruido * np.random.normal(0,1,len(t))
    suma_tonos = tonos + ruido
    return suma_tonos

def suma_musical(wav, amp_ruido):
    """Suma señal musical con ruido blanco de distintas amplitudes.
    ----
    Parametros:
    wav: string - ruta del archivo .wav
    amp_ruido: float - amplitud del ruido blanco
    ----
    Salida:
    señal: array de señal generada"""

    señal, fs= sf.read(wav)
    t = np.arange(0, len(señal)/fs, 1/fs)
    ruido = amp_ruido * np.random.normal(0,1,len(t))
    suma_musical = señal + ruido
    return suma_musical

def filtro_media_movil(x, m, p):
    """
    Aplica un filtro de promedio móvil de longitud L a una señal x.
    
    Parámetros:
    ------------
    x : ndarray - señal de entrada (1D, array de valores reales o complejos).
    m : int - longitud (muestras) de la ventana de promedio.
    p : int - cantidad de veces que se aplica el filtro
    
    Retorna:
    --------
    y : ndarray - señal suavizada.
    """
    if m < 1:
        raise ValueError("La longitud m debe ser mayor o igual a 1")

    kernel = np.ones(m) / m

    veces = np.arange(p)
    for i in veces:
        y = scipy.fftconvolve(x, kernel, mode='same')

    return y

def filtro_peine(x,a,b,c):
    """Aplica un filtro peine a una señal x.
    ----
    Parametros:
    x: array de señal de entrada
    a,b,c: float - parámetros constantes del filtro peine
    ---
    Salida:
    y: array de señal pasada por el filtro peine"""
    
    n = len(x)
    h = np.zeros(n)
    d = scipy.unit_impulse(n, idx=0)
    d1 = scipy.unit_impulse(n, idx=1)
    for i in range(n):
        h[i] = a + b*d[i] + c*d1[i]

    y = scipy.fftconvolve(x,h,mode='same')

    return y


"""Graficar una o varias señales temporales.

Graficar uno o varios espectros de Fourier.

Determinar la respuesta en frecuencia de un sistema Hw dado un par de señales de entrada Xw y salida Yw."""

import matplotlib.pyplot as plt

def graficar_temp(t, data, mismo_eje=True):
    """
    Grafica señales temporales usando argumentos variables.
    ----
    Parametros:
    t: array con valores de tiempo
    data: N arreglos de datos (señal1, señal2, ...)
    mismo_eje: bool
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
    
    # 1. Generar el eje de frecuencias correcto
    # freq = [0, 1, ..., n/2] * fs / n
    freq = np.fft.rfftfreq(n, d=1/fs)
    
    # 2. Calcular las transformadas (usamos rfft para señales reales)
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
        if cant == 1: axes = [axes]

        for i, magnitud in enumerate(espectros):
            axes[i].plot(freq, magnitud, color=f'C{i}')
            axes[i].set_title(f'Espectro Señal {i+1}')
            axes[i].set_ylabel('Magnitud')
            axes[i].grid(True)

        plt.xlabel('Frecuencia [Hz]')
        plt.tight_layout()
        plt.show()