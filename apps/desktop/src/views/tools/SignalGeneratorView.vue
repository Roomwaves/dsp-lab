<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import { ref, computed } from 'vue';
import { IconPlus, IconTrash, IconDownload, IconPlayerPlay } from '@tabler/icons-vue';
import { api } from '../../services/api';
import WaveformPlot from '../../components/plots/WaveformPlot.vue';
import SpectrumPlot from '../../components/plots/SpectrumPlot.vue';

const { t } = useI18n();

// Signal type: 'sine' | 'square' | 'triangle' | 'white-noise' | 'pink-noise' | 'sweep'
const signalType = ref('sine');

// Tone entries for multi-tone (sine mode)
interface ToneEntry {
  frequency: number;
  amplitude: number;
}

const tones = ref<ToneEntry[]>([
  { frequency: 440, amplitude: 1.0 },
]);

// Single wave / noise parameters
const frequency = ref(440);
const amplitude = ref(0.8);

// Sweep parameters
const fStart = ref(20);
const fEnd = ref(20000);
const sweepType = ref('linear'); // 'linear' | 'logarithmic'

// Global Settings
const fs = ref(44100);
const duration = ref(1.0);
const snrDb = ref(20);
const applyNoise = ref(false);

const fsOptions = [8000, 22050, 44100, 48000];
const durationOptions = [0.5, 1, 2, 5];

// Result
const samples = ref<number[]>([]);
const fftFrequencies = ref<number[]>([]);
const fftMagnitudes = ref<number[]>([]);
const isLoading = ref(false);
const error = ref<string | null>(null);

const hasSamples = computed(() => samples.value.length > 0);

function addTone() {
  tones.value.push({ frequency: 1000, amplitude: 0.5 });
}

function removeTone(i: number) {
  if (tones.value.length > 1) tones.value.splice(i, 1);
}

async function generate() {
  isLoading.value = true;
  error.value = null;
  try {
    const params: any = {
      signalType: signalType.value,
      fs: fs.value,
      duration: duration.value,
      amplitude: amplitude.value,
      applyNoise: applyNoise.value,
      snrDb: snrDb.value,
    };

    if (signalType.value === 'sine') {
      params.frequencies = tones.value.map(t => t.frequency);
      params.amplitudes = tones.value.map(t => t.amplitude);
    } else if (signalType.value === 'square' || signalType.value === 'triangle') {
      params.frequency = frequency.value;
      params.amplitude = amplitude.value;
    } else if (signalType.value === 'white-noise' || signalType.value === 'pink-noise') {
      params.amplitude = amplitude.value;
    } else if (signalType.value === 'sweep') {
      params.fStart = fStart.value;
      params.fEnd = fEnd.value;
      params.sweepType = sweepType.value;
      params.amplitude = amplitude.value;
    }

    const result = await api.generateSignal(params);
    samples.value = result.samples;

    // Compute FFT for spectrum
    const fftResult = await api.fft(samples.value, fs.value);
    fftFrequencies.value = fftResult.frequencies;
    fftMagnitudes.value = fftResult.magnitudes;
  } catch (e) {
    error.value = (e as Error).message;
  } finally {
    isLoading.value = false;
  }
}

async function exportWav() {
  if (!hasSamples.value) return;
  try {
    await api.downloadAudio(samples.value, fs.value);
  } catch (e) {
    error.value = (e as Error).message;
  }
}
</script>

<template>
  <div class="sg-view">
    <!-- TopBar -->
    <div class="sg-topbar">
      <span class="sg-title">{{ t('sidebar.signal_generator') }}</span>
      <span class="sg-subtitle">Generador de señales de precisión: Seno, Cuadrada, Triangular, Ruido y Barridos.</span>
    </div>

    <!-- Inputs section -->
    <div class="inputs-section">
      <!-- Dynamic Parameters Panel -->
      <div class="tones-panel">
        <div class="panel-header">
          <span class="panel-title">Tipo de Señal</span>
          <!-- Signal Type Dropdown -->
          <div class="type-selector-wrapper">
            <select id="sg-type-select" v-model="signalType" class="select-ctrl select-type">
              <option value="sine">Seno / Multi-tono</option>
              <option value="square">Onda Cuadrada</option>
              <option value="triangle">Onda Triangular</option>
              <option value="white-noise">Ruido Blanco</option>
              <option value="pink-noise">Ruido Rosa</option>
              <option value="sweep">Barrido de Frecuencia (Sweep)</option>
            </select>
          </div>
        </div>

        <!-- SINE / MULTI-TONE PARAMETERS -->
        <div v-if="signalType === 'sine'" class="signal-config-container">
          <div class="tones-table-header">
            <span class="section-subtitle">Tonos puros a sumar:</span>
            <button class="icon-btn" title="Agregar tono" @click="addTone">
              <IconPlus size="13" />
            </button>
          </div>
          <div class="tones-table">
            <div class="table-head">
              <span>Freq (Hz)</span>
              <span>Amplitud</span>
              <span></span>
            </div>
            <div
              v-for="(tone, i) in tones"
              :key="i"
              class="table-row"
            >
              <input
                :id="`sg-freq-${i}`"
                v-model.number="tone.frequency"
                type="number"
                min="1"
                :max="fs / 2"
                step="1"
                class="num-input"
                placeholder="440"
              />
              <input
                :id="`sg-amp-${i}`"
                v-model.number="tone.amplitude"
                type="number"
                min="0"
                max="1"
                step="0.01"
                class="num-input"
                placeholder="1.0"
              />
              <button class="icon-btn danger" :disabled="tones.length === 1" @click="removeTone(i)">
                <IconTrash size="12" />
              </button>
            </div>
          </div>
        </div>

        <!-- SQUARE / TRIANGLE WAVE PARAMETERS -->
        <div v-else-if="signalType === 'square' || signalType === 'triangle'" class="signal-config-container grid-params">
          <div class="param-row">
            <div class="param-info">
              <label for="sg-freq-single" class="param-label">Frecuencia (Hz)</label>
              <input id="sg-freq-single" v-model.number="frequency" type="number" min="1" :max="fs / 2" class="num-input-small" />
            </div>
            <input
              v-model.number="frequency"
              type="range"
              min="20"
              :max="fs / 2"
              step="1"
              class="slider-param"
            />
          </div>
          <div class="param-row">
            <div class="param-info">
              <label for="sg-amp-single" class="param-label">Amplitud</label>
              <input id="sg-amp-single" v-model.number="amplitude" type="number" min="0" max="1" step="0.01" class="num-input-small" />
            </div>
            <input
              v-model.number="amplitude"
              type="range"
              min="0"
              max="1"
              step="0.01"
              class="slider-param"
            />
          </div>
        </div>

        <!-- NOISE PARAMETERS -->
        <div v-else-if="signalType === 'white-noise' || signalType === 'pink-noise'" class="signal-config-container grid-params">
          <div class="param-row">
            <div class="param-info">
              <label for="sg-amp-noise" class="param-label">Amplitud (Pico / RMS)</label>
              <input id="sg-amp-noise" v-model.number="amplitude" type="number" min="0" max="1" step="0.01" class="num-input-small" />
            </div>
            <input
              v-model.number="amplitude"
              type="range"
              min="0"
              max="1"
              step="0.01"
              class="slider-param"
            />
          </div>
        </div>

        <!-- SWEEP PARAMETERS -->
        <div v-else-if="signalType === 'sweep'" class="signal-config-container grid-params">
          <div class="sweep-params-row">
            <div class="param-row">
              <div class="param-info">
                <label for="sg-fstart" class="param-label">Freq Inicial (Hz)</label>
                <input id="sg-fstart" v-model.number="fStart" type="number" min="1" :max="fs / 2" class="num-input-small" />
              </div>
              <input
                v-model.number="fStart"
                type="range"
                min="20"
                :max="fs / 2"
                step="1"
                class="slider-param"
              />
            </div>
            <div class="param-row">
              <div class="param-info">
                <label for="sg-fend" class="param-label">Freq Final (Hz)</label>
                <input id="sg-fend" v-model.number="fEnd" type="number" min="1" :max="fs / 2" class="num-input-small" />
              </div>
              <input
                v-model.number="fEnd"
                type="range"
                min="20"
                :max="fs / 2"
                step="1"
                class="slider-param"
              />
            </div>
          </div>
          
          <div class="sweep-params-row">
            <div class="param-row flex-item">
              <label for="sg-sweep-type-select" class="param-label">Tipo de Barrido</label>
              <select id="sg-sweep-type-select" v-model="sweepType" class="select-ctrl select-sweep-type">
                <option value="linear">Lineal</option>
                <option value="logarithmic">Logarítmico</option>
              </select>
            </div>
            <div class="param-row flex-item">
              <div class="param-info">
                <label for="sg-amp-sweep" class="param-label">Amplitud</label>
                <input id="sg-amp-sweep" v-model.number="amplitude" type="number" min="0" max="1" step="0.01" class="num-input-small" />
              </div>
              <input
                v-model.number="amplitude"
                type="range"
                min="0"
                max="1"
                step="0.01"
                class="slider-param"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Settings column -->
      <div class="settings-col">
        <!-- Sample Rate -->
        <div class="setting-group">
          <label class="setting-label" for="sg-fs-select">Fs</label>
          <select id="sg-fs-select" v-model.number="fs" class="select-ctrl">
            <option v-for="f in fsOptions" :key="f" :value="f">{{ f >= 1000 ? f / 1000 + ' kHz' : f + ' Hz' }}</option>
          </select>
        </div>

        <!-- Duration -->
        <div class="setting-group">
          <label class="setting-label" for="sg-dur-select">Duración</label>
          <select id="sg-dur-select" v-model.number="duration" class="select-ctrl">
            <option v-for="d in durationOptions" :key="d" :value="d">{{ d }} s</option>
          </select>
        </div>

        <!-- Noise -->
        <div class="setting-group">
          <label class="setting-label" for="sg-noise-toggle">Agregar Ruido</label>
          <input id="sg-noise-toggle" v-model="applyNoise" type="checkbox" class="checkbox" />
        </div>

        <div v-if="applyNoise" class="setting-group">
          <label class="setting-label" for="sg-snr-slider">SNR: {{ snrDb }} dB</label>
          <input
            id="sg-snr-slider"
            v-model.number="snrDb"
            type="range"
            min="-10"
            max="60"
            step="1"
            class="slider"
          />
        </div>

        <!-- Generate button -->
        <button
          id="sg-generate-btn"
          class="btn btn-primary"
          :disabled="isLoading || (signalType === 'sine' && tones.length === 0)"
          @click="generate"
        >
          <IconPlayerPlay size="13" />
          {{ isLoading ? 'Generando…' : 'Generar' }}
        </button>

        <!-- Export button -->
        <button
          id="sg-export-btn"
          class="btn btn-secondary"
          :disabled="!hasSamples"
          @click="exportWav"
        >
          <IconDownload size="13" />
          Export .wav
        </button>
      </div>
    </div>

    <!-- Error -->
    <div v-if="error" class="error-banner">{{ error }}</div>

    <!-- Plots -->
    <div class="plots-area">
      <div class="plot-wrapper">
        <div class="plot-title">Waveform</div>
        <WaveformPlot
          v-if="hasSamples"
          id="sg-waveform-plot"
          :samples="samples"
          :fs="fs"
          :height="0"
          class="plot-fill"
        />
        <div v-else class="empty-plot">—</div>
      </div>

      <div class="plot-wrapper">
        <div class="plot-title">Spectrum</div>
        <SpectrumPlot
          v-if="hasSamples"
          id="sg-spectrum-plot"
          :frequencies="fftFrequencies"
          :magnitudes="fftMagnitudes"
          :db-scale="true"
          :log-frequency="true"
          :height="0"
          class="plot-fill"
        />
        <div v-else class="empty-plot">—</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.sg-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  overflow: hidden;
}

/* TopBar */
.sg-topbar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 20px;
  border-bottom: 0.5px solid var(--color-border);
  flex-shrink: 0;
}

.sg-title {
  font-size: 13px;
  font-weight: 600;
}

.sg-subtitle {
  font-size: 11px;
  color: var(--color-text-secondary);
}

/* Inputs section */
.inputs-section {
  display: flex;
  gap: 16px;
  padding: 14px 20px;
  flex-shrink: 0;
  border-bottom: 0.5px solid var(--color-border);
}

/* Tones panel */
.tones-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.panel-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-secondary);
}

.icon-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 6px;
  border: 0.5px solid var(--color-border);
  background: var(--color-bg-elevated);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: background 0.12s, color 0.12s;
}

.icon-btn:hover:not(:disabled) {
  background: var(--color-accent-dim, rgba(0, 217, 126, 0.15));
  color: var(--color-accent);
}

.icon-btn.danger:hover:not(:disabled) {
  background: rgba(239, 68, 68, 0.12);
  color: #EF4444;
}

.icon-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.tones-table {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.table-head {
  display: grid;
  grid-template-columns: 1fr 1fr 28px;
  gap: 8px;
  font-size: 10px;
  color: var(--color-text-tertiary);
  padding: 0 2px;
}

.table-row {
  display: grid;
  grid-template-columns: 1fr 1fr 28px;
  gap: 8px;
  align-items: center;
}

.num-input {
  width: 100%;
  padding: 5px 8px;
  background: var(--color-bg-elevated);
  border: 0.5px solid var(--color-border);
  border-radius: var(--border-radius-md);
  color: var(--color-text-primary);
  font-size: 12px;
  font-family: var(--font-mono);
}

/* Settings col */
.settings-col {
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-width: 180px;
  flex-shrink: 0;
}

.setting-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.setting-label {
  font-size: 11px;
  color: var(--color-text-secondary);
  min-width: 76px;
  flex-shrink: 0;
}

.select-ctrl {
  flex: 1;
  background: var(--color-bg-elevated);
  border: 0.5px solid var(--color-border);
  border-radius: var(--border-radius-md);
  color: var(--color-text-primary);
  font-size: 11px;
  padding: 4px 8px;
}

.checkbox {
  accent-color: var(--color-accent);
  cursor: pointer;
}

.slider {
  flex: 1;
  accent-color: var(--color-accent);
  cursor: pointer;
}

.btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 7px 14px;
  border-radius: var(--border-radius-md);
  font-size: 12px;
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition: opacity 0.15s;
}

.btn:disabled {
  opacity: 0.38;
  cursor: not-allowed;
}

.btn-primary {
  background: var(--color-accent);
  color: #fff;
}

.btn-secondary {
  background: var(--color-bg-elevated);
  color: var(--color-text-primary);
  border: 0.5px solid var(--color-border);
}

/* Error */
.error-banner {
  margin: 0 20px 8px;
  padding: 8px 12px;
  background: rgba(239, 68, 68, 0.1);
  border: 0.5px solid rgba(239, 68, 68, 0.4);
  border-radius: var(--border-radius-md);
  font-size: 12px;
  color: #EF4444;
  flex-shrink: 0;
}

/* Plots */
.plots-area {
  flex: 1;
  display: grid;
  grid-template-rows: 1fr 1fr;
  gap: 8px;
  padding: 12px 16px;
  overflow: hidden;
}

.plot-wrapper {
  display: flex;
  flex-direction: column;
  gap: 4px;
  overflow: hidden;
}

.plot-title {
  font-size: 10px;
  font-weight: 600;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  flex-shrink: 0;
}

.plot-fill {
  flex: 1;
  height: 100% !important;
}

.plot-wrapper :deep(.spectrum-container),
.plot-wrapper :deep(.waveform-container) {
  height: 100% !important;
}

.empty-plot {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: var(--color-text-tertiary);
  background: var(--color-bg-secondary);
  border-radius: var(--border-radius-md);
  border: 0.5px solid var(--color-border);
}

/* New layout containers & params styles */
.signal-config-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
  background: var(--color-bg-secondary);
  border: 0.5px solid var(--color-border);
  border-radius: var(--border-radius-md);
  padding: 12px;
}

.type-selector-wrapper {
  display: flex;
  align-items: center;
}

.select-type {
  font-weight: 500;
  border-color: var(--color-accent);
}

.tones-table-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 4px;
}

.section-subtitle {
  font-size: 11px;
  color: var(--color-text-secondary);
}

.grid-params {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.param-row {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.param-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.param-label {
  font-size: 11px;
  color: var(--color-text-secondary);
  font-weight: 500;
}

.num-input-small {
  width: 70px;
  padding: 3px 6px;
  background: var(--color-bg-elevated);
  border: 0.5px solid var(--color-border);
  border-radius: var(--border-radius-md);
  color: var(--color-text-primary);
  font-size: 11px;
  font-family: var(--font-mono);
  text-align: right;
}

.slider-param {
  width: 100%;
  accent-color: var(--color-accent);
  cursor: pointer;
}

.sweep-params-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.select-sweep-type {
  width: 100%;
  padding: 4px 8px;
  background: var(--color-bg-elevated);
}

.flex-item {
  justify-content: flex-start;
}
</style>
