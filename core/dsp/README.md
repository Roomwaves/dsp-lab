# Módulo DSP Core — Guía de Desarrollo y Pruebas

Este directorio contiene el motor matemático y de procesamiento digital de señales (DSP) del proyecto. El desarrollo de las funciones pendientes se organiza mediante issues y se valida a través de pruebas unitarias automatizadas.

---

## 🛠️ Flujo de Trabajo

1. **Implementación de Funciones:** Las firmas de las funciones se encuentran definidas en los archivos de `core/dsp/`. Para cada tarea, se debe reemplazar la excepción `raise NotImplementedError` con la implementación correspondiente, respetando los tipos de entrada y salida (type hints).
2. **Ejecución de Pruebas:** Cada función cuenta con pruebas unitarias asociadas en `core/dsp/tests/` para verificar su correcto comportamiento matemático antes de ser integrada a la rama principal.

---

## 🧪 Comandos para la Ejecución de Tests

Las pruebas se ejecutan desde la raíz del monorepo utilizando `pytest`.

### Ejecutar todas las pruebas unitarias:
```bash
npm run test:python
```
o de forma directa:
```bash
uv run pytest
```

### Ejecutar las pruebas de un archivo específico:
```bash
uv run pytest core/dsp/tests/test_signals.py
```

### Ejecutar una prueba específica:
```bash
uv run pytest core/dsp/tests/test_signals.py -k "test_noise_snr_approximate"
```

---

## 📋 Relación de Funciones, Issues y Criterios de Aceptación

### 📡 1. Módulo `signals.py` (Issue #4)

#### `generate_pure_tones(frequencies, amplitudes, fs, duration)`
* **Prueba:** `test_tones_output_length`
  * *Verificación:* La longitud del arreglo retornado debe ser exactamente igual a $\lfloor fs \times duration \rfloor$.
* **Prueba:** `test_tones_single_frequency`
  * *Verificación:* Para un único tono de frecuencia $f$, el pico del espectro obtenido mediante la FFT debe ubicarse en el bin correspondiente a $f$.
* **Prueba:** `test_tones_amplitude_scaling`
  * *Verificación:* Duplicar el parámetro de amplitud de un tono debe duplicar el valor de la señal en el dominio del tiempo de manera lineal.
* **Prueba:** `test_tones_zero_amplitude`
  * *Verificación:* Si la amplitud de los tonos es cero, la señal resultante debe ser un vector nulo.

#### `add_white_noise(signal, snr_db)`
* **Prueba:** `test_noise_snr_approximate`
  * *Verificación:* El ruido blanco gaussiano agregado debe cumplir con la Relación Señal-Ruido (SNR) especificada en decibelios (dB) con una tolerancia de $\pm 2\text{ dB}$.
* **Prueba:** `test_noise_output_length`
  * *Verificación:* La longitud del arreglo con ruido debe coincidir exactamente con la de la señal original.
* **Prueba:** `test_noise_different_each_call`
  * *Verificación:* Dos llamadas consecutivas con los mismos parámetros deben generar señales numéricamente distintas debido a la naturaleza estocástica del ruido.

---

### 🧮 2. Módulo `analysis.py` (Issues #5, #6 y #7)

#### `compute_fft(signal, fs)`
* **Prueba:** `test_fft_dc_signal`
  * *Verificación:* Una señal de nivel constante (DC) debe tener su pico de magnitud espectral en $0\text{ Hz}$.
* **Prueba:** `test_fft_sine_peak`
  * *Verificación:* Para un tono senoidal puro, la frecuencia correspondiente a la magnitud máxima de la FFT debe coincidir con la frecuencia del tono.
* **Prueba:** `test_fft_frequency_range` y `test_fft_nyquist`
  * *Verificación:* El vector de frecuencias debe comenzar en $0\text{ Hz}$ y su frecuencia máxima no debe exceder la frecuencia de Nyquist ($fs / 2$).
* **Prueba:** `test_fft_lengths_match`
  * *Verificación:* El vector de frecuencias y el de magnitudes espectrales deben tener la misma dimensión.
* **Prueba:** `test_fft_positive_magnitudes`
  * *Verificación:* Todas las magnitudes espectrales deben ser reales y no negativas.

#### `compute_frequency_response(x, y, fs)`
* **Prueba:** `test_freq_response_identity_system`
  * *Verificación:* Si $y[n] = x[n]$ (sistema identidad), la magnitud de la respuesta al impulso $|H(\omega)|$ debe ser aproximadamente $1.0$ en todas las frecuencias.
* **Prueba:** `test_freq_response_lengths_match`
  * *Verificación:* El vector de frecuencias y el vector de respuesta $H(\omega)$ deben coincidir en longitud.
* **Prueba:** `test_freq_response_complex`
  * *Verificación:* La respuesta en frecuencia $H(\omega)$ debe consistir en coeficientes complejos.

#### `compute_magnitude_db(H)`
* **Prueba:** `test_magnitude_db_units`
  * *Verificación:* Comprobación de la escala logarítmica: $|H| = 1 \to 0\text{ dB}$, $|H| = 10 \to 20\text{ dB}$, $|H| = 0.1 \to -20\text{ dB}$. Debe manejar magnitudes nulas de forma segura sin producir desbordamientos.

#### `compute_phase(H)`
* **Prueba:** `test_phase_range`
  * *Verificación:* Los valores de fase deben estar contenidos dentro del intervalo de valores principales $[-\pi, \pi]$ radianes.

#### `convolve_time(signal, h)` y `convolve_frequency(signal, h)`
* **Prueba:** `test_convolve_time_output_length` y `test_convolve_freq_output_length`
  * *Verificación:* La convolución lineal (en el tiempo o mediante multiplicación de espectros con el padding adecuado) debe retornar un vector de longitud $L + M - 1$, donde $L$ es la longitud de la señal y $M$ la longitud del filtro.
* **Prueba:** `test_convolve_equivalence`
  * *Verificación:* Ambos métodos (convolución temporal y frecuencial) deben producir resultados numéricamente equivalentes.
* **Prueba:** `test_convolve_time_delta` y `test_convolve_freq_delta`
  * *Verificación:* La convolución con un impulso unitario $\delta[n] = [1.0]$ debe reproducir la señal de entrada sin modificaciones.

---

### 📊 3. Módulo `coherence.py` (Issues #8 y #9)

#### `compute_psd(signal, fs, n_segments)` y `compute_cpsd(x, y, fs, n_segments)`
* **Prueba:** `test_psd_real_positive`
  * *Verificación:* La estimación de la Densidad Espectral de Potencia (PSD) propia $G_{xx}(\omega)$ debe retornar valores reales y no negativos.
* **Prueba:** `test_cpsd_same_signal`
  * *Verificación:* Si las dos señales de entrada son la misma ($x = y$), la Densidad Espectral de Potencia Cruzada (CPSD) $G_{xy}(\omega)$ debe ser equivalente a la PSD $G_{xx}(\omega)$.
* **Prueba:** `test_psd_white_noise_flat`
  * *Verificación:* Al evaluar ruido blanco, la PSD promedio debe presentar un espectro de potencia plano, caracterizado por una desviación estándar reducida respecto a la media.

#### `compute_coherence(x, y, fs, n_segments)`
* **Prueba:** `test_coherence_range`
  * *Verificación:* La coherencia cuadrática $\gamma_{xy}^2(\omega)$ debe estar acotada entre $0.0$ y $1.0$ en todo el espectro.
* **Prueba:** `test_coherence_identity`
  * *Verificación:* La coherencia espectral entre una señal y sí misma debe ser igual a $1.0$.
* **Prueba:** `test_coherence_independent`
  * *Verificación:* La coherencia entre dos procesos de ruido independientes y no correlacionados debe ser cercana a cero (promedio inferior a $0.3$).

---

### 📉 4. Módulo `plots.py` (Issue #10)

#### `plot_signal(signal, fs, title, ax)`
* **Prueba:** `test_plot_signal_returns_figure` y `test_plot_signal_xlabel`
  * *Verificación:* Debe retornar un objeto `Figure` de matplotlib. El eje X debe incluir la etiqueta de tiempo ("Time (s)" o "Tiempo (s)").

#### `plot_spectrum(frequencies, magnitudes, title, ax, db)`
* **Prueba:** `test_plot_spectrum_returns_figure` y `test_plot_spectrum_db_mode`
  * *Verificación:* Retorna un objeto `Figure`. En el modo logarítmico (`db=True`), el eje Y debe indicar que la unidad es "dB".

#### `plot_frequency_response(frequencies, H, title, fig)`
* **Prueba:** `test_plot_freq_response_has_two_axes`
  * *Verificación:* Debe retornar un objeto `Figure` con al menos dos ejes correspondientes a los subplots de módulo y fase.

#### `plot_coherence(frequencies, coherence, title, ax)`
* **Prueba:** `test_plot_coherence_ylim`
  * *Verificación:* Retorna una `Figure`. El eje Y del gráfico de coherencia debe tener fijado su límite en el rango $[0.0, 1.0]$.
