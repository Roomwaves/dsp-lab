import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf
import scipy.signal as scipy

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

def filtro_peine(x,a,b,c):
    """Aplica un filtro peine a una señal x.
    ----
    Parametros:
    x: array de señal de entrada´
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

fs = 44100
f_test = np.array([440, 880, 1320]) # Frecuencias: La, La octava, Mi
a_test = np.array([1.0, 0.5, 0.2])  # Amplitudes decrecientes
muestras = 0.05                     # 50ms para visualización clara

# 1. Generar señal base
x = suma_tonos_puros(f_test, a_test, muestras, amp_ruido=0.1, fs=fs)

# 2. Aplicar tu filtro peine
# a, b, c son tus constantes del filtro
y = filtro_peine(x, a=0.5, b=1.0, c=0.5)

# --- IMPRESIÓN DE DATOS ---
print(f"Longitud de la señal: {len(x)} muestras")
print(f"Valor máximo entrada: {np.max(x):.4f}")
print(f"Valor máximo salida: {np.max(y):.4f}")

# --- CONFIGURACIÓN DE GRÁFICOS ---
t = np.arange(0, muestras, 1/fs)

plt.figure(figsize=(12, 6))

# Gráfico Temporal
plt.subplot(2, 1, 1)
plt.plot(t, x, label='Entrada (Tonos + Ruido)', alpha=0.7)
plt.plot(t, y, label='Salida (Filtro Peine)', color='orange', linewidth=1.5)
plt.title('Señal en el Tiempo')
plt.xlabel('Tiempo [s]')
plt.ylabel('Amplitud')
plt.legend()
plt.grid(True)

# Gráfico Espectral (FFT)
plt.subplot(2, 1, 2)
freqs = np.fft.rfftfreq(len(x), 1/fs)
X_mag = np.abs(np.fft.rfft(x))
Y_mag = np.abs(np.fft.rfft(y))

plt.plot(freqs, X_mag, label='Espectro Entrada', alpha=0.6)
plt.plot(freqs, Y_mag, label='Espectro Salida (Filtrado)', color='red')
plt.title('Análisis de Frecuencia')
plt.xlabel('Frecuencia [Hz]')
plt.ylabel('Magnitud')
plt.xlim(0, 3000) # Zoom en la zona de interés de los tonos
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()