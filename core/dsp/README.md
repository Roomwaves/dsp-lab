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
uv run pytest core/dsp/tests/test_signals.py -k "test_snr_approximate"
```

---

## 📋 Relación de Funciones, Issues y Criterios de Aceptación

### 🎛️ Módulo `filters.py`

#### Issue #1 — `moving_average()` y `MovingAverageFilter`
* **Prueba:** `TestMovingAverage::test_dc_preservation`
  * *Verificación:* Una señal constante filtrada debe seguir siendo constante tras el transitorio inicial.
* **Prueba:** `TestMovingAverage::test_output_length`
  * *Verificación:* La longitud del arreglo filtrado es igual a la señal de entrada para ventanas $M \in \{3, 8, 16, 32\}$.
* **Prueba:** `TestMovingAverage::test_m1_is_identity`
  * *Verificación:* Con $M=1$, la señal de salida es idéntica a la señal de entrada.
* **Prueba:** `TestMovingAverage::test_passes_increase_smoothness`
  * *Verificación:* Múltiples pasadas consecutivas aumentan el nivel de suavizado (menor varianza).
* **Prueba:** `TestMovingAverage::test_does_not_modify_input`
  * *Verificación:* La señal de entrada no sufre modificaciones *in-place*.
* **Prueba:** `TestMovingAverage::test_reduces_noise`
  * *Verificación:* La señal filtrada presenta una varianza en su derivada (diferencias sucesivas) menor que la señal original.
* **Prueba:** `TestMovingAverageFilter::test_block_output_length`
  * *Verificación:* La longitud del bloque de salida coincide con el tamaño del bloque procesado ($256, 512, 1024$).
* **Prueba:** `TestMovingAverageFilter::test_block_consistency_with_batch`
  * *Verificación:* El procesamiento en bloques es equivalente al procesamiento de la señal completa (batch).
* **Prueba:** `TestMovingAverageFilter::test_reset_restores_initial_state`
  * *Verificación:* La llamada a `reset()` restaura el estado inicial del buffer del filtro.
* **Prueba:** `TestMovingAverageFilter::test_state_persists_between_blocks`
  * *Verificación:* El buffer interno evita discontinuidades en las uniones de bloques.

#### Issue #2 — `comb_filter()` y `CombFilterState`
* **Prueba:** `TestCombFilter::test_zero_coefficients`
  * *Verificación:* Con coeficientes nulos, la salida consiste enteramente en ceros.
* **Prueba:** `TestCombFilter::test_identity_b0_only`
  * *Verificación:* Con $b_0=1$, $b_1=0$, $b_2=0$, la salida es idéntica a la entrada.
* **Prueba:** `TestCombFilter::test_output_length`
  * *Verificación:* La longitud de salida coincide exactamente con la de la entrada.
* **Prueba:** `TestCombFilter::test_impulse_response`
  * *Verificación:* Ante una entrada impulso unitario $\delta[n]$, la salida corresponde a la secuencia de coeficientes $[b_0, b_1, b_2, 0, 0, \dots]$.
* **Prueba:** `TestCombFilter::test_delay_two`
  * *Verificación:* Con $b_0=0, b_1=0, b_2=1$, la salida es la señal de entrada demorada en $2$ muestras.
* **Prueba:** `TestCombFilter::test_does_not_modify_input`
  * *Verificación:* La señal recibida como entrada no es modificada.

#### Issue #3 — `apply_fir()`, `truncate_fir()` y `FIRFilter`
* **Prueba:** `TestApplyFIR::test_delta_coefficients_is_identity`
  * *Verificación:* Con un único coeficiente unitario, la salida es idéntica a la entrada.
* **Prueba:** `TestApplyFIR::test_output_length`
  * *Verificación:* La longitud de salida coincide con la de la entrada.
* **Prueba:** `TestApplyFIR::test_equivalence_with_moving_average`
  * *Verificación:* Un filtro FIR con coeficientes constantes e iguales a $1/M$ equivale al filtro de media móvil de ventana $M$.
* **Prueba:** `TestApplyFIR::test_does_not_modify_input`
  * *Verificación:* La señal de entrada no sufre modificaciones *in-place*.
* **Prueba:** `TestTruncateFIR::test_output_length`
  * *Verificación:* Truncar a $N$ coeficientes produce un arreglo de tamaño $N$.
* **Prueba:** `TestTruncateFIR::test_values_are_first_n`
  * *Verificación:* Los coeficientes conservados corresponden a los primeros $N$ coeficientes originales.
* **Prueba:** `TestTruncateFIR::test_full_length_returns_original`
  * *Verificación:* Si $N$ es igual a la cantidad de coeficientes, se retorna una copia completa.
* **Prueba:** `TestTruncateFIR::test_does_not_modify_original`
  * *Verificación:* El arreglo original de coeficientes no se modifica.
* **Prueba:** `TestTruncateFIR::test_invalid_n_raises`
  * *Verificación:* El truncado con valores de $N < 1$ o $N > \text{longitud de coeficientes}$ eleva excepciones de tipo `ValueError`.

---

### 📡 Módulo `signals.py`

#### Issue #4 — `generate_pure_tones()`, `add_white_noise()` y `generate_impulse()`
* **Prueba:** `TestGeneratePureTones::test_output_length`
  * *Verificación:* La señal generada tiene una longitud igual a $\lfloor fs \times duration \rfloor$.
* **Prueba:** `TestGeneratePureTones::test_single_frequency_peak`
  * *Verificación:* Un tono puro a una frecuencia $f$ presenta su pico espectral máximo en la frecuencia correspondiente del espectro de amplitud.
* **Prueba:** `TestGeneratePureTones::test_amplitude_scaling`
  * *Verificación:* Modificar linealmente la amplitud de los tonos escala correspondientemente la señal en el tiempo.
* **Prueba:** `TestGeneratePureTones::test_zero_amplitude`
  * *Verificación:* Amplitud nula genera una señal compuesta únicamente de ceros.
* **Prueba:** `TestGeneratePureTones::test_multiple_frequencies`
  * *Verificación:* La suma de tonos presenta picos de amplitud detectables en cada una de las frecuencias de la lista.
* **Prueba:** `TestGeneratePureTones::test_mismatched_lengths_raises`
  * *Verificación:* Diferente número de elementos en las listas de frecuencias y amplitudes eleva un `ValueError`.
* **Prueba:** `TestAddWhiteNoise::test_output_length`
  * *Verificación:* La señal ruidosa de salida tiene la misma longitud que la de entrada.
* **Prueba:** `TestAddWhiteNoise::test_snr_approximate`
  * *Verificación:* La potencia del ruido inyectado se ajusta para cumplir con la SNR en dB solicitada (tolerancia de $\pm 3\text{ dB}$).
* **Prueba:** `TestAddWhiteNoise::test_high_snr_barely_changes_signal`
  * *Verificación:* A una SNR elevada (ej. $60\text{ dB}$), la señal de salida es prácticamente idéntica a la señal de entrada.
* **Prueba:** `TestAddWhiteNoise::test_randomness_between_calls`
  * *Verificación:* Llamadas repetidas devuelven valores numéricamente diferentes debido a la aleatoriedad.
* **Prueba:** `TestAddWhiteNoise::test_does_not_modify_input`
  * *Verificación:* No modifica el arreglo de entrada.
* **Prueba:** `TestGenerateImpulse::test_output_length`
  * *Verificación:* La señal generada tiene el tamaño especificado.
* **Prueba:** `TestGenerateImpulse::test_single_one_at_zero`
  * *Verificación:* Por defecto, el valor unitario ($1.0$) se ubica en el índice 0, y el resto de la señal consiste en ceros.
* **Prueba:** `TestGenerateImpulse::test_single_one_at_delay`
  * *Verificación:* Al especificar un retardo $d$, el valor unitario se posiciona exactamente en el índice $d$.
* **Prueba:** `TestGenerateImpulse::test_sum_is_one`
  * *Verificación:* La suma total de los elementos del arreglo es igual a $1.0$.
* **Prueba:** `TestGenerateImpulse::test_invalid_delay_raises`
  * *Verificación:* Si el retardo especificado está fuera del rango válido ($d < 0$ o $d \ge \text{length}$), se eleva un `ValueError`.

---

### 🧮 Módulo `analysis.py`

#### Issue #5 — `compute_fft()`
* **Prueba:** `TestComputeFFT::test_lengths_match`
  * *Verificación:* El vector de frecuencias y el de magnitudes espectrales coinciden en tamaño.
* **Prueba:** `TestComputeFFT::test_frequency_range`
  * *Verificación:* Las frecuencias del espectro unilateral van de $0$ a $\le fs/2$.
* **Prueba:** `TestComputeFFT::test_magnitudes_non_negative`
  * *Verificación:* Las magnitudes espectrales calculadas son reales y no negativas.
* **Prueba:** `TestComputeFFT::test_dc_signal_peak_at_zero`
  * *Verificación:* Una señal constante concentra su magnitud máxima espectral en $0\text{ Hz}$.
* **Prueba:** `TestComputeFFT::test_sine_peak_frequency`
  * *Verificación:* Un tono senoidal puro presenta su máximo en el bin de frecuencia correcto.
* **Prueba:** `TestComputeFFT::test_output_types`
  * *Verificación:* Los vectores retornados consisten en números reales.
* **Prueba:** `TestComputeFFT::test_nyquist_not_exceeded`
  * *Verificación:* Ningún bin de frecuencia supera la frecuencia de Nyquist ($fs / 2$).

#### Issue #6 — Respuesta en Frecuencia (Mapeo de Variables y Conversión)
* **Prueba:** `TestFrequencyResponse::test_freq_response_identity_system`
  * *Verificación:* En un sistema de identidad ($y[n] = x[n]$), la magnitud espectral es $|H(\omega)| \approx 1.0$ para todas las frecuencias.
* **Prueba:** `TestFrequencyResponse::test_freq_response_lengths_match`
  * *Verificación:* Coincidencia de dimensiones en los vectores resultantes.
* **Prueba:** `TestFrequencyResponse::test_freq_response_complex`
  * *Verificación:* La respuesta en frecuencia $H(\omega)$ está compuesta de coeficientes complejos.
* **Prueba:** `TestFrequencyResponse::test_magnitude_db_units`
  * *Verificación:* Verificación de escala en dB ($20\log_{10}(|H|)$) con manejo de valor cero.
* **Prueba:** `TestFrequencyResponse::test_phase_range`
  * *Verificación:* Los valores de fase en radianes pertenecen al intervalo principal $[-\pi, \pi]$.
* **Prueba:** `TestFrequencyResponse::test_freq_response_frequency_range`
  * *Verificación:* Frecuencias acotadas entre $0$ y $fs/2$.

#### Issue #7 — `convolve_time()` y `convolve_frequency()`
* **Prueba:** `TestConvolveTime::test_output_length` y `TestConvolveFrequency::test_output_length`
  * *Verificación:* La longitud del resultado es exactamente igual a $L + M - 1$ (convolución lineal completa).
* **Prueba:** `TestConvolveTime::test_delta_h_is_identity` y `TestConvolveFrequency::test_delta_h_is_identity`
  * *Verificación:* La convolución con un impulso unitario discreto $\delta[n] = [1.0]$ da como resultado la señal original.
* **Prueba:** `TestConvolveTime::test_output_is_ndarray`
  * *Verificación:* La salida se devuelve como un arreglo de NumPy.
* **Prueba:** `TestConvolveFrequency::test_equivalence_with_convolve_time`
  * *Verificación:* Validación numérica de equivalencia entre convolución en tiempo y multiplicación en frecuencia (con tolerancia de `atol=1e-8`).
* **Prueba:** `TestConvolveFrequency::test_output_is_real`
  * *Verificación:* La parte imaginaria residual producto de la IFFT es insignificante.
* **Prueba:** `TestConvolveFrequency::test_zero_padding_correctness`
  * *Verificación:* El algoritmo aplica zero-padding hasta longitud $L + M - 1$ previo al cálculo de la FFT, previniendo el fenómeno de aliasing circular en el dominio del tiempo.

---

### 📊 Módulo `coherence.py`

#### Issue #8 y #9 — `compute_psd()`, `compute_cpsd()` y `compute_coherence()`
* **Prueba:** `TestPSDAndCPSD::test_psd_real_positive`
  * *Verificación:* La PSD propia es real y no negativa.
* **Prueba:** `TestPSDAndCPSD::test_psd_frequency_range` y `test_psd_lengths_match`
  * *Verificación:* Rango de frecuencias de $0$ a $fs/2$ y concordancia de tamaños.
* **Prueba:** `TestPSDAndCPSD::test_cpsd_lengths_match`
  * *Verificación:* Longitud del vector de frecuencias y CPSD compleja son idénticas.
* **Prueba:** `TestPSDAndCPSD::test_cpsd_same_signal`
  * *Verificación:* Si la entrada y salida son la misma señal, la CPSD coincide con la PSD propia.
* **Prueba:** `TestPSDAndCPSD::test_psd_white_noise_flat`
  * *Verificación:* La potencia espectral de ruido blanco estimada mediante periodogramas promediados es razonablemente plana.
* **Prueba:** `TestCoherence::test_coherence_range`
  * *Verificación:* Los valores de coherencia espectral pertenecen al rango lógico $[0.0, 1.0]$.
* **Prueba:** `TestCoherence::test_coherence_identity`
  * *Verificación:* Coherencia unitaria ($1.0$) al correlacionar una señal consigo misma.
* **Prueba:** `TestCoherence::test_coherence_independent`
  * *Verificación:* Coherencia promedio baja ($< 0.3$) entre señales de ruido estadísticamente independientes y no correlacionadas.
* **Prueba:** `TestCoherence::test_coherence_lengths_match`
  * *Verificación:* Tamaños de vectores coincidentes.
* **Prueba:** `TestCoherence::test_coherence_real`
  * *Verificación:* La coherencia calculada es real y no compleja.

---

### 📉 Módulo `plots.py`

#### Issue #10 — Graficación (`plot_signal`, `plot_spectrum`, `plot_frequency_response`, `plot_coherence`)
* **Prueba:** `TestPlotSignal::test_no_crash` y `test_returns_figure`
  * *Verificación:* La función no genera excepciones y retorna un objeto `matplotlib.figure.Figure`.
* **Prueba:** `TestPlotSpectrum::test_no_crash`, `test_returns_figure` y `test_db_mode_no_crash`
  * *Verificación:* No genera excepciones en modo lineal o en escala de decibelios, y retorna un objeto `Figure`.
* **Prueba:** `TestPlotFrequencyResponse::test_no_crash`, `test_returns_figure` y `test_has_two_axes`
  * *Verificación:* Retorna un objeto `Figure` con al menos 2 ejes correspondientes a los subplots de magnitud y fase.
* **Prueba:** `TestPlotCoherence::test_no_crash` y `test_returns_figure`
  * *Verificación:* Grafica la coherencia cuadrática y retorna una `Figure` sin lanzar excepciones.
