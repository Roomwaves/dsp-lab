# This file imports from core/dsp package
import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf
import scipy.signal as scipy

def graficar_temp(t, data, mismo_eje=True):
    """
    Grafica señales temporales usando argumentos variables.
    ----
    Parametros:
    t: array con valores de tiempo
    data: N arreglos de datos (señal1, señal2, ...)
    mismo_eje: bool
    ----
    Salida:
    Gráficos de señales temporales para cada señal dada.
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
    ----
    Parámetros:
    t: array con valores de tiempo (para calcular el eje de frecuencias)
    data: N arreglos de datos (señal1, señal2, ...)
    fs: frecuencia de muestreo
    mismo_eje: bool - si True, todas las señales en el mismo gráfico; si False, gráficos separados
    ----
    Salida:
    Gráficos de espectro de frecuencia para cada señal dada.
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

def rta_frecuencia(x,y):
    """Calcula la respuesta en frecuencia de un sistema dado su entrada y salida.
    ----
    Parametros:
    x: array de señal de entrada
    y: array de señal de salida
    ---
    Salida:
    H: array con la respuesta en frecuencia (compleja)"""

    X = np.fft.rfft(x)
    Y = np.fft.rfft(y)
    
    X[X == 0] = 1e-10 # Evita división por cero
    
    H = Y / X
    return H

def suma_tonos_puros(f, a, duracion, amp_ruido, fs=44100):
    """Suma tonos puros con ruido blanco de distintas amplitudes.
    ----
    Parametros:
    f: array-like - frecuencias de los tonos
    a: array-like - amplitudes de cada tono (misma longitud que f)
    duracion: float - duración de la señal en segundos
    amp_ruido: float - amplitud del ruido blanco
    fs: int - frecuencia de muestreo, por defecto 44100 Hz
    ----
    Salida:
    suma_tonos: array - señal generada
    """
    f = np.atleast_1d(f)
    a = np.atleast_1d(a)
    
    t = np.arange(0, duracion, 1/fs)
    tonos = np.zeros(len(t))
    
    for i in range(len(f)):
        tonos += a[i] * np.sin(2 * np.pi * f[i] * t)
        
    ruido = amp_ruido * np.random.normal(0, 1, len(t))
    return tonos + ruido

def suma_musical(wav, amp_ruido):
    """Suma señal musical con ruido blanco adaptándose a canales mono o estéreo.
    ----
    Parametros:
    wav: string - ruta del archivo .wav
    amp_ruido: float - amplitud del ruido blanco
    ----
    Salida:
    señal: array de señal generada"""

    señal, fs = sf.read(wav)
    ruido = amp_ruido * np.random.normal(0, 1, señal.shape) # Generar ruido con la misma forma (shape) que la señal (soporta estéreo)
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
    h : ndarray - respuesta al impulso del filtro de promedio móvil aplicado p veces.
    """

    if m < 1:
        raise ValueError("La longitud m debe ser mayor o igual a 1")
    h = np.ones(m) / m
    y = x.copy()
    for i in range(p):
        y = scipy.fftconvolve(y, h, mode='same')
    return y, h

def filtro_peine(x, a, b, c):
    """Aplica un filtro peine a una señal x respetando la ecuación del profesor.
    ----
    Parametros:
    x: array de señal de entrada
    a, b, c: float - parámetros constantes del filtro peine
    ---
    Salida:
    y: array de señal pasada por el filtro peine.
    h: array con la respuesta al impulso del filtro peine aplicado a x."""
    
    n = len(x)
    d = np.zeros(n)
    d[0] = 1.0
    d1 = np.zeros(n)
    if n > 1:
        d1[1] = 1.0
    h = a + b * d + c * d1
    y = scipy.fftconvolve(x, h, mode='same')
    return y, h

def filtro_fir(x):
    """Aplica un filtro FIR a una señal x usando coeficientes predefinidos.
    ----
    Parametros:
    x: array de señal de entrada
    fs: int - frecuencia de muestreo (por defecto 44100 Hz)
    ---
    Salida:
    y: array de señal pasada por el filtro FIR.
    h: array con la respuesta al impulso del filtro FIR aplicado a x."""
    
    file_name = r'archivos\fir_hamming_1000Hz.npy' # Coeficientes del filtro FIR
    h = np.load(file_name)
    a = [1.0]  # Denominador para filtro FIR
    y = scipy.lfilter(h, a, x) # Aplica el filtro usando lfilter

    return y, h


# PRUEBA DE LAS FILTROS Y GRÁFICOS

fs = 44100
duracion = 2.0
t_vector = np.arange(0, duracion, 1/fs)

f_tonos = [500, 1000, 5000]
a_tonos = [1.0, 0.5, 0.2]
x_tonos = suma_tonos_puros(f_tonos, a_tonos, duracion, amp_ruido=0.05)
x_musical = suma_musical(r'archivos\musica_ruido_0.01.wav', amp_ruido=0.02)

y_tonos_media, h_media = filtro_media_movil(x_tonos, m=20, p=2)
y_tonos_peine, h_peine = filtro_peine(x_tonos, a=0.1, b=0.5, c=0.4)
y_tonos_fir, h_fir = filtro_fir(x_tonos)

y_musical_media, h_m_media = filtro_media_movil(x_musical, m=20, p=2)
y_musical_peine, h_m_peine = filtro_peine(x_musical, a=0.1, b=0.5, c=0.4)
y_musical_fir, h_m_fir = filtro_fir(x_musical)

slice_plot = slice(0, 1000) 
graficar_temp(t_vector[slice_plot], 
              [x_tonos[slice_plot], y_tonos_media[slice_plot], y_tonos_peine[slice_plot], y_tonos_fir[slice_plot]], 
              mismo_eje=False)
graficar_frecuencias(t_vector, [x_tonos, y_tonos_media, y_tonos_peine, y_tonos_fir], fs, mismo_eje=False)

t_musical = np.arange(0, len(x_musical)/fs, 1/fs)
graficar_temp(t_musical[slice_plot], 
              [x_musical[slice_plot], y_musical_media[slice_plot], y_musical_peine[slice_plot], y_musical_fir[slice_plot]], 
              mismo_eje=False)
graficar_frecuencias(t_musical, [x_musical, y_musical_media, y_musical_peine, y_musical_fir], fs, mismo_eje=False)

def filtrar_frecuencia_manual(x, b):
    # Padding a N+M-1 para que la circular sea igual a la lineal
    n_fft = len(x) + len(b) - 1
    X = np.fft.fft(x, n=n_fft)
    B = np.fft.fft(b, n=n_fft)
    Y = X * B
    return np.fft.ifft(Y).real[:len(x)]

# --- 1. FILTRO FIR ---
y_tonos_fir_tiempo, h_fir = filtro_fir(x_tonos)
y_tonos_fir_frec = filtrar_frecuencia_manual(x_tonos, h_fir)
error_fir = np.linalg.norm(y_tonos_fir_tiempo - y_tonos_fir_frec)

# --- 2. FILTRO PEINE ---
y_tonos_peine_tiempo, h_peine = filtro_peine(x_tonos, a=0.1, b=0.5, c=0.4)
y_tonos_peine_frec = filtrar_frecuencia_manual(x_tonos, h_peine)
error_peine = np.linalg.norm(y_tonos_peine_tiempo - y_tonos_peine_frec)

# --- 3. FILTRO MEDIA MÓVIL (Para 1 pasada, p=1)* ---
y_tonos_media_tiempo, h_media = filtro_media_movil(x_tonos, m=20, p=1)
y_tonos_media_frec = filtrar_frecuencia_manual(x_tonos, h_media)
error_media = np.linalg.norm(y_tonos_media_tiempo - y_tonos_media_frec)

# --- IMPRIMIR RESULTADOS PARA EL INFORME ---
print(f"Error numérico Filtro FIR: {error_fir:.2e}")
print(f"Error numérico Filtro Peine: {error_peine:.2e}")
print(f"Error numérico Filtro Media Móvil: {error_media:.2e}")