<script setup lang="ts">
import { ref, computed } from 'vue';
import { IconPlus, IconTrash, IconDownload, IconPlayerPlay } from '@tabler/icons-vue';
import { api } from '../../../services/api';
import WaveformPlot from '../../plots/WaveformPlot.vue';
import SpectrumPlot from '../../plots/SpectrumPlot.vue';

// Tone entries
interface ToneEntry {
  frequency: number;
  amplitude: number;
}

const tones = ref<ToneEntry[]>([
  { frequency: 440, amplitude: 1.0 },
]);

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
  if (tones.value.length === 0) return;
  isLoading.value = true;
  error.value = null;
  try {
    const freqs = tones.value.map(t => t.frequency);
    const amps = tones.value.map(t => t.amplitude);

    let result = await api.generatePureTones(freqs, amps, fs.value, duration.value);
    samples.value = result.samples;

    if (applyNoise.value) {
      result = await api.addWhiteNoise(result.samples, fs.value, snrDb.value);
      samples.value = result.samples;
    }

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
  <div class="sg-panel">
    <!-- Inputs section -->
    <div class="inputs-section">
      <!-- Tones table -->
      <div class="tones-panel">
        <div class="panel-header">
          <span class="panel-title">Tonos</span>
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
          <label class="setting-label" for="sg-noise-toggle">Ruido</label>
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

        <!-- Action buttons -->
        <div class="actions-row">
          <button
            id="sg-generate-btn"
            class="btn btn-primary"
            :disabled="isLoading || tones.length === 0"
            @click="generate"
          >
            <IconPlayerPlay size="13" />
            {{ isLoading ? 'Generando…' : 'Generar' }}
          </button>

          <button
            id="sg-export-btn"
            class="btn btn-secondary"
            :disabled="!hasSamples"
            @click="exportWav"
          >
            <IconDownload size="13" />
            Export
          </button>
        </div>
      </div>
    </div>

    <!-- Error -->
    <div v-if="error" class="error-banner">{{ error }}</div>

    <!-- Plots -->
    <div class="plots-area-drawer">
      <div class="plot-wrapper">
        <div class="plot-title">Waveform</div>
        <WaveformPlot
          v-if="hasSamples"
          id="sg-waveform-plot"
          :samples="samples"
          :fs="fs"
          :height="130"
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
          :height="130"
        />
        <div v-else class="empty-plot">—</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.sg-panel {
  display: flex;
  flex-direction: column;
  width: 100%;
}

/* Inputs section */
.inputs-section {
  display: flex;
  gap: 20px;
  padding-bottom: 16px;
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
  font-size: 11px;
  font-weight: 600;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.icon-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border-radius: 4px;
  border: 0.5px solid var(--color-border);
  background: var(--color-bg-elevated);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: background 0.12s, color 0.12s;
}

.icon-btn:hover:not(:disabled) {
  background: var(--color-accent-dim);
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
  color: var(--color-text-secondary);
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
  padding: 4px 6px;
  background: var(--color-bg-elevated);
  border: 0.5px solid var(--color-border);
  border-radius: var(--border-radius-md);
  color: var(--color-text-primary);
  font-size: 11px;
  font-family: var(--font-mono);
}

/* Settings col */
.settings-col {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 220px;
  flex-shrink: 0;
}

.setting-group {
  display: flex;
  align-items: center;
  gap: 10px;
  justify-content: space-between;
}

.setting-label {
  font-size: 11px;
  color: var(--color-text-secondary);
}

.select-ctrl {
  background: var(--color-bg-elevated);
  border: 0.5px solid var(--color-border);
  border-radius: var(--border-radius-md);
  color: var(--color-text-primary);
  font-size: 11px;
  padding: 3px 6px;
  cursor: pointer;
}

.checkbox {
  accent-color: var(--color-accent);
  cursor: pointer;
}

.slider {
  width: 100px;
  accent-color: var(--color-accent);
  cursor: pointer;
}

.actions-row {
  display: flex;
  gap: 8px;
  margin-top: 4px;
}

.btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 5px 10px;
  border-radius: var(--border-radius-md);
  font-size: 11px;
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
  margin-top: 8px;
  padding: 6px 10px;
  background: rgba(239, 68, 68, 0.1);
  border: 0.5px solid rgba(239, 68, 68, 0.4);
  border-radius: var(--border-radius-md);
  font-size: 11px;
  color: #EF4444;
}

/* Plots */
.plots-area-drawer {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 16px;
}

.plot-wrapper {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.plot-title {
  font-size: 10px;
  font-weight: 600;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.empty-plot {
  height: 130px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  color: var(--color-text-secondary);
  background: var(--color-bg-secondary);
  border-radius: var(--border-radius-md);
  border: 0.5px solid var(--color-border);
}
</style>
