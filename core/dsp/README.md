# Guía de Trabajo y Pruebas — Módulo DSP Core

¡Hola equipo! En este directorio se encuentra el motor matemático y de procesamiento de señales de nuestro TP de DSP. Para asegurar que todas las funciones matemáticas y gráficos implementados sean correctos y se integren perfectamente, utilizaremos **Desarrollo Guiado por Pruebas (TDD)**.

Este documento explica cómo deben trabajar en el código, cómo ejecutar los tests unitarios y qué verifica cada prueba para cada una de las funciones asignadas en los Issues de GitHub.

---

## 🛠️ Cómo Trabajar

1. **Identifica tu tarea:** Revisa en GitHub el número de Issue que tienes asignado.
2. **Ubica el archivo:** El código de procesamiento vive en `core/dsp/`. No debes modificar la estructura de las carpetas ni las firmas de las funciones.
3. **Escribe tu solución:** Abre el archivo correspondiente en `core/dsp/` (ej. `signals.py`, `analysis.py`, etc.), busca la función indicada y reemplaza la línea `raise NotImplementedError(...)` con tu implementación matemática.
4. **Verifica tus cambios:** Corre los tests unitarios. Cuando pasen a verde, tu tarea estará lista.

---

## 🧪 Cómo Ejecutar los Tests

Para ejecutar las pruebas en tu entorno local, asegúrate de estar parado en la raíz del repositorio monorepo y corre cualquiera de las siguientes opciones:

### Ejecutar todos los tests de Python:
```bash
npm run test:python
```
*(O de forma directa usando `uv`:)*
```bash
uv run pytest
```

### Ejecutar solo un archivo de pruebas específico:
Si estás trabajando en un módulo específico y quieres evitar la salida de las demás pruebas, puedes indicar la ruta del archivo de test:
```bash
uv run pytest core/dsp/tests/test_signals.py
```

### Ejecutar un test en particular:
```bash
uv run pytest core/dsp/tests/test_signals.py -k "test_noise_snr_approximate"
```

---

## 📋 Resumen de Requerimientos y Tests por Función

A continuación se detalla qué debe resolver cada función y qué criterios de éxito verifican los tests unitarios automatizados:

### 📡 1. Módulo `signals.py` (Issue #4)

#### `generate_pure_tones(frequencies, amplitudes, fs, duration)`
* **Propósito:** Genera un arreglo de NumPy que contenga la suma de varios tonos senoidales puros a partir de listas de frecuencias y amplitudes.
* **Qué verifican los tests:**
  * `test_tones_output_length`: La longitud del arreglo retornado debe ser exactamente $f_s \times \text{duration}$.
  * `test_tones_single_frequency`: Si se genera un tono a una frecuencia (ej. $440\text{ Hz}$), el pico espectral más alto en la FFT debe corresponder a esa frecuencia.
  * `test_tones_amplitude_scaling`: El escalado debe ser lineal (duplicar el parámetro de amplitud debe duplicar la amplitud de la señal en el tiempo).
  * `test_tones_zero_amplitude`: Si todas las amplitudes son $0.0$, la señal resultante debe ser un arreglo de ceros.

#### `add_white_noise(signal, snr_db)`
* **Propósito:** Toma una señal y le suma ruido blanco gaussiano para alcanzar una Relación Señal-Ruido (SNR) específica en decibelios (dB).
* **Qué verifican los tests:**
  * `test_noise_snr_approximate`: Calcula la potencia de la señal original y la potencia del ruido inyectado, verificando que la SNR resultante medida esté dentro de una tolerancia de $\pm 2\text{ dB}$ del valor solicitado.
  * `test_noise_output_length`: La longitud de la señal ruidosa debe ser idéntica a la señal original.
  * `test_noise_different_each_call`: Garantiza que el ruido sea estocástico real (dos llamadas con los mismos parámetros deben retornar ruidos con valores numéricos distintos).

---

### 🧮 2. Módulo `analysis.py` (Issues #5, #6 y #7)

#### `compute_fft(signal, fs)`
* **Propósito:** Calcula la Transformada de Fourier Discreta (DFT) unilateral de la señal. Debe retornar la tupla de arreglos `(frecuencias, magnitudes)`.
* **Qué verifican los tests:**
  * `test_fft_dc_signal`: Una señal de valor constante (DC) debe concentrar su energía espectral únicamente en la frecuencia $0\text{ Hz}$.
  * `test_fft_sine_peak`: Un tono senoidal puro debe registrar su máximo valor espectral en la frecuencia del tono.
  * `test_fft_frequency_range` / `test_fft_nyquist`: El vector de frecuencias debe comenzar exactamente en $0\text{ Hz}$ y no exceder la frecuencia de Nyquist ($f_s / 2$).
  * `test_fft_positive_magnitudes`: Las magnitudes del espectro deben ser reales y estrictamente no negativas ($\ge 0$).

#### `compute_frequency_response(x, y, fs)`
* **Propósito:** Estima la respuesta en frecuencia compleja del sistema mediante la división espectral $H(\omega) = \frac{Y(\omega)}{X(\omega)}$. Retorna `(frecuencias, H_complejo)`.
* **Qué verifican los tests:**
  * `test_freq_response_identity_system`: Si la entrada y la salida son idénticas ($y[n] = x[n]$), la magnitud $|H(\omega)|$ debe ser aproximadamente $1.0$ para todas las frecuencias.
  * `test_freq_response_complex`: La respuesta en frecuencia resultante $H$ debe contener valores complejos (`complex128`).

#### `compute_magnitude_db(H)`
* **Propósito:** Convierte los valores de la respuesta compleja en magnitud expresada en decibelios mediante la fórmula: $20 \log_{10}(|H|)$.
* **Qué verifican los tests:**
  * `test_magnitude_db_units`: Comprueba valores exactos de conversión: $|H|=1 \to 0\text{ dB}$, $|H|=10 \to 20\text{ dB}$, $|H|=0.1 \to -20\text{ dB}$. Debe evitar fallos por división por cero en magnitudes nulas.

#### `compute_phase(H)`
* **Propósito:** Calcula la fase en radianes a partir de la respuesta espectral compleja $H$.
* **Qué verifican los tests:**
  * `test_phase_range`: El vector de fase debe estar estrictamente acotado en el intervalo estándar de $[-\pi, \pi]$ radianes.

#### `convolve_time(signal, h)` y `convolve_frequency(signal, h)`
* **Propósito:** Realizan la convolución lineal entre la señal de entrada y la respuesta al impulso del filtro $h[n]$. Una se calcula directamente en el tiempo, y la otra utilizando la propiedad de la convolución en frecuencia (multiplicación espectral de FFTs de tamaño adecuado).
* **Qué verifican los tests:**
  * `test_convolve_time_output_length` / `test_convolve_freq_output_length`: Ambas funciones deben retornar un arreglo de longitud exacta $L + M - 1$ (donde $L$ es la longitud de la señal y $M$ la longitud de $h$).
  * `test_convolve_equivalence`: Compara los resultados numéricos de ambos métodos y asegura que la convolución temporal y frecuencial (con el correcto padding de ceros) den valores virtualmente idénticos.
  * `test_convolve_time_delta` / `test_convolve_freq_delta`: La convolución con un delta de Kronecker unitario ($\delta[n] = [1.0]$) debe reproducir exactamente la señal original.

---

### 📊 3. Módulo `coherence.py` (Issues #8 y #9)

#### `compute_psd(signal, fs, n_segments)` y `compute_cpsd(x, y, fs, n_segments)`
* **Propósito:** Estiman la Densidad Espectral de Potencia (PSD) y la Densidad Espectral de Potencia Cruzada (CPSD) utilizando el método de promediado de periodogramas (Welch).
* **Qué verifican los tests:**
  * `test_psd_real_positive`: La PSD propia $G_{xx}(\omega)$ debe arrojar valores reales y no negativos.
  * `test_cpsd_same_signal`: Si $x == y$, entonces la PSD cruzada $G_{xy}(\omega)$ debe ser numéricamente igual a la PSD propia $G_{xx}(\omega)$.
  * `test_psd_white_noise_flat`: Comprueba que al alimentar ruido blanco, el perfil de potencia espectral promediado sea relativamente plano (desviación estándar acotada).

#### `compute_coherence(x, y, fs, n_segments)`
* **Propósito:** Calcula la coherencia cuadrática entre dos señales aplicando la fórmula:
  $$\gamma_{xy}^2(\omega) = \frac{|G_{xy}(\omega)|^2}{G_{xx}(\omega) \cdot G_{yy}(\omega)}$$
* **Qué verifican los tests:**
  * `test_coherence_range`: La coherencia debe estar matemáticamente confinada entre $0.0$ y $1.0$.
  * `test_coherence_identity`: La coherencia entre una señal y sí misma debe ser idéntica a $1.0$ en todos los bines de frecuencia.
  * `test_coherence_independent`: Si $x$ e $y$ son señales de ruido blanco totalmente independientes y desconectadas, el promedio de su coherencia estimada en frecuencia debe ser muy bajo (cercano a cero, $< 0.3$).

---

### 📉 4. Módulo `plots.py` (Issue #10)

* **Propósito:** Generar gráficos en el dominio del tiempo y de la frecuencia usando `matplotlib`.
* **Qué verifican los tests:**
  * Todos los gráficos deben retornar una instancia válida de `matplotlib.figure.Figure`.
  * `test_plot_signal_xlabel`: El eje X del gráfico temporal debe etiquetarse correctamente como `"Time (s)"` o `"Tiempo (s)"`.
  * `test_plot_spectrum_db_mode`: Si se activa el modo en decibelios en el espectro, el eje Y debe indicar `"dB"`.
  * `test_plot_freq_response_has_two_axes`: La respuesta en frecuencia debe graficarse obligatoriamente con dos subplots acoplados (uno para la Magnitud en dB y otro para la Fase en radianes/grados).
  * `test_plot_coherence_ylim`: El gráfico de coherencia debe tener fijados estáticamente los límites del eje Y en la escala lógica de $[0.0, 1.0]$.
