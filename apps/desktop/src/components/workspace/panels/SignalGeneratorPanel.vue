<script setup lang="ts">
import { IconPlus, IconTrash, IconDownload, IconPlayerPlay, IconVolume, IconVolumeOff } from '@tabler/icons-vue';
import { useSignalStore } from '../../../stores/useSignalStore';
import WaveformPlot from '../../plots/WaveformPlot.vue';
import SpectrumPlot from '../../plots/SpectrumPlot.vue';

const signalStore = useSignalStore();

const fsOptions = [8000, 22050, 44100, 48000, 96000];
const durationOptions = [0.5, 1, 2, 5];
</script>

<template>
  <div class="sg-panel">
    <!-- Inputs section -->
    <div class="inputs-section">
      <!-- Dynamic Parameters Panel -->
      <div class="tones-panel">
        <div class="panel-header">
          <span class="panel-title">Tipo de Señal</span>
          <!-- Signal Type Dropdown -->
          <div class="type-selector-wrapper">
            <select id="sg-type-select" v-model="signalStore.signalType" class="select-ctrl select-type">
              <option value="sine">Seno / Multi-tono</option>
              <option value="square">Onda Cuadrada</option>
              <option value="triangle">Onda Triangular</option>
              <option value="white-noise">Ruido Blanco</option>
              <option value="pink-noise">Ruido Rosa</option>
              <option value="sweep">Barrido (Sweep)</option>
            </select>
          </div>
        </div>

        <!-- SINE / MULTI-TONE PARAMETERS -->
        <div v-if="signalStore.signalType === 'sine'" class="signal-config-container">
          <div class="tones-table-header">
            <span class="section-subtitle">Tonos puros a sumar:</span>
            <button class="icon-btn" title="Agregar tono" @click="signalStore.addTone">
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
              v-for="(tone, i) in signalStore.tones"
              :key="i"
              class="table-row"
            >
              <input
                :id="`sg-freq-${i}`"
                v-model.number="tone.frequency"
                type="number"
                min="1"
                :max="signalStore.fs / 2"
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
              <button class="icon-btn danger" :disabled="signalStore.tones.length === 1" @click="signalStore.removeTone(i)">
                <IconTrash size="12" />
              </button>
            </div>
          </div>
        </div>

        <!-- SQUARE PARAMETERS -->
        <div v-else-if="signalStore.signalType === 'square'" class="signal-config-container grid-params">
          <div class="param-row">
            <div class="param-info">
              <label for="sg-freq-square" class="param-label">Frecuencia (Hz)</label>
              <input id="sg-freq-square" v-model.number="signalStore.frequency" type="number" min="1" :max="signalStore.fs / 2" class="num-input-small" />
            </div>
            <input
              v-model.number="signalStore.frequency"
              type="range"
              min="20"
              :max="signalStore.fs / 2"
              step="1"
              class="slider-param"
            />
          </div>
          <div class="param-row">
            <div class="param-info">
              <label for="sg-amp-square" class="param-label">Amplitud</label>
              <input id="sg-amp-square" v-model.number="signalStore.amplitude" type="number" min="0" max="1" step="0.01" class="num-input-small" />
            </div>
            <input
              v-model.number="signalStore.amplitude"
              type="range"
              min="0"
              max="1"
              step="0.01"
              class="slider-param"
            />
          </div>
          <div class="param-row">
            <div class="param-info">
              <label for="sg-duty-square" class="param-label">Ciclo de Trabajo (Duty {{ Math.round(signalStore.duty * 100) }}%)</label>
              <input id="sg-duty-square" v-model.number="signalStore.duty" type="number" min="0.01" max="0.99" step="0.01" class="num-input-small" />
            </div>
            <input
              v-model.number="signalStore.duty"
              type="range"
              min="0.01"
              max="0.99"
              step="0.01"
              class="slider-param"
            />
          </div>
        </div>

        <!-- TRIANGLE PARAMETERS -->
        <div v-else-if="signalStore.signalType === 'triangle'" class="signal-config-container grid-params">
          <div class="param-row">
            <div class="param-info">
              <label for="sg-freq-tri" class="param-label">Frecuencia (Hz)</label>
              <input id="sg-freq-tri" v-model.number="signalStore.frequency" type="number" min="1" :max="signalStore.fs / 2" class="num-input-small" />
            </div>
            <input
              v-model.number="signalStore.frequency"
              type="range"
              min="20"
              :max="signalStore.fs / 2"
              step="1"
              class="slider-param"
            />
          </div>
          <div class="param-row">
            <div class="param-info">
              <label for="sg-amp-tri" class="param-label">Amplitud</label>
              <input id="sg-amp-tri" v-model.number="signalStore.amplitude" type="number" min="0" max="1" step="0.01" class="num-input-small" />
            </div>
            <input
              v-model.number="signalStore.amplitude"
              type="range"
              min="0"
              max="1"
              step="0.01"
              class="slider-param"
            />
          </div>
          <div class="param-row">
            <div class="param-info">
              <label for="sg-width-tri" class="param-label">Simetría Ramp / Width ({{ Math.round(signalStore.width * 100) }}%)</label>
              <input id="sg-width-tri" v-model.number="signalStore.width" type="number" min="0" max="1" step="0.01" class="num-input-small" />
            </div>
            <input
              v-model.number="signalStore.width"
              type="range"
              min="0"
              max="1"
              step="0.01"
              class="slider-param"
            />
          </div>
        </div>

        <!-- NOISE PARAMETERS -->
        <div v-else-if="signalStore.signalType === 'white-noise' || signalStore.signalType === 'pink-noise'" class="signal-config-container grid-params">
          <div class="param-row">
            <div class="param-info">
              <label for="sg-amp-noise" class="param-label">Amplitud (Pico / RMS)</label>
              <input id="sg-amp-noise" v-model.number="signalStore.amplitude" type="number" min="0" max="1" step="0.01" class="num-input-small" />
            </div>
            <input
              v-model.number="signalStore.amplitude"
              type="range"
              min="0"
              max="1"
              step="0.01"
              class="slider-param"
            />
          </div>
        </div>

        <!-- SWEEP PARAMETERS -->
        <div v-else-if="signalStore.signalType === 'sweep'" class="signal-config-container grid-params">
          <div class="sweep-params-row">
            <div class="param-row">
              <div class="param-info">
                <label for="sg-fstart" class="param-label">Freq Inicial (Hz)</label>
                <input id="sg-fstart" v-model.number="signalStore.fStart" type="number" min="1" :max="signalStore.fs / 2" class="num-input-small" />
              </div>
              <input
                v-model.number="signalStore.fStart"
                type="range"
                min="20"
                :max="signalStore.fs / 2"
                step="1"
                class="slider-param"
              />
            </div>
            <div class="param-row">
              <div class="param-info">
                <label for="sg-fend" class="param-label">Freq Final (Hz)</label>
                <input id="sg-fend" v-model.number="signalStore.fEnd" type="number" min="1" :max="signalStore.fs / 2" class="num-input-small" />
              </div>
              <input
                v-model.number="signalStore.fEnd"
                type="range"
                min="20"
                :max="signalStore.fs / 2"
                step="1"
                class="slider-param"
              />
            </div>
          </div>
          
          <div class="sweep-params-row">
            <div class="param-row flex-item">
              <label for="sg-sweep-type-select" class="param-label">Tipo de Barrido</label>
              <select id="sg-sweep-type-select" v-model="signalStore.sweepType" class="select-ctrl select-sweep-type">
                <option value="linear">Lineal</option>
                <option value="logarithmic">Logarítmico</option>
              </select>
            </div>
            <div class="param-row flex-item">
              <div class="param-info">
                <label for="sg-amp-sweep" class="param-label">Amplitud</label>
                <input id="sg-amp-sweep" v-model.number="signalStore.amplitude" type="number" min="0" max="1" step="0.01" class="num-input-small" />
              </div>
              <input
                v-model.number="signalStore.amplitude"
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
          <select id="sg-fs-select" v-model.number="signalStore.fs" class="select-ctrl">
            <option v-for="f in fsOptions" :key="f" :value="f">{{ f >= 1000 ? f / 1000 + ' kHz' : f + ' Hz' }}</option>
          </select>
        </div>

        <!-- Duration -->
        <div class="setting-group">
          <label class="setting-label" for="sg-dur-select">Duración</label>
          <select id="sg-dur-select" v-model.number="signalStore.duration" class="select-ctrl">
            <option v-for="d in durationOptions" :key="d" :value="d">{{ d }} s</option>
          </select>
        </div>

        <!-- Noise -->
        <div class="setting-group">
          <label class="setting-label" for="sg-noise-toggle">Ruido</label>
          <input id="sg-noise-toggle" v-model="signalStore.applyNoise" type="checkbox" class="checkbox" />
        </div>

        <div v-if="signalStore.applyNoise" class="setting-group">
          <label class="setting-label" for="sg-snr-slider">SNR: {{ signalStore.snrDb }} dB</label>
          <input
            id="sg-snr-slider"
            v-model.number="signalStore.snrDb"
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
            :disabled="signalStore.isLoading || (signalStore.signalType === 'sine' && signalStore.tones.length === 0)"
            @click="signalStore.generate"
          >
            <IconPlayerPlay size="13" />
            {{ signalStore.isLoading ? 'Generando…' : 'Generar' }}
          </button>

          <button
            v-if="signalStore.hasSamples"
            class="btn btn-secondary"
            @click="signalStore.isPlaying ? signalStore.stopAudio() : signalStore.playAudio()"
          >
            <component :is="signalStore.isPlaying ? IconVolumeOff : IconVolume" size="13" />
            {{ signalStore.isPlaying ? 'Detener' : 'Escuchar' }}
          </button>

          <button
            id="sg-export-btn"
            class="btn btn-secondary"
            :disabled="!signalStore.hasSamples"
            @click="signalStore.exportWav"
          >
            <IconDownload size="13" />
            Export
          </button>
        </div>
      </div>
    </div>

    <!-- Error -->
    <div v-if="signalStore.error" class="error-banner">{{ signalStore.error }}</div>

    <!-- Plots -->
    <div class="plots-area-drawer">
      <div class="plot-wrapper">
        <div class="plot-title">Waveform (Forma de Onda)</div>
        <WaveformPlot
          v-if="signalStore.hasSamples"
          id="sg-waveform-plot"
          :samples="signalStore.samples"
          :fs="signalStore.fs"
          :height="130"
        />
        <div v-else class="empty-plot">Sin señal generada</div>
      </div>

      <div class="plot-wrapper">
        <div class="plot-title">Spectrum (Espectro FFT)</div>
        <SpectrumPlot
          v-if="signalStore.hasSamples"
          id="sg-spectrum-plot"
          :frequencies="signalStore.fftFrequencies"
          :magnitudes="signalStore.fftMagnitudes"
          :db-scale="true"
          :log-frequency="true"
          :height="130"
        />
        <div v-else class="empty-plot">Sin señal generada</div>
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
  justify-content: space-between;
  align-items: center;
}

.panel-title {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--color-text-secondary);
}

.select-ctrl {
  background: var(--surface-3, #1e1e21);
  border: 0.5px solid var(--color-border);
  color: var(--text-white, #ffffff);
  border-radius: var(--border-radius-md);
  padding: 4px 8px;
  font-size: 11px;
  font-family: inherit;
  cursor: pointer;
  outline: none;
}

.select-ctrl option {
  background: var(--surface-3, #1e1e21);
  color: var(--text-white, #ffffff);
}

.select-type {
  font-weight: 600;
  color: var(--color-text-primary);
}

.signal-config-container {
  background: var(--color-bg-secondary);
  border-radius: var(--border-radius-md);
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.grid-params {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.sweep-params-row {
  display: flex;
  gap: 12px;
}

.flex-item {
  flex: 1;
}

.section-subtitle {
  font-size: 11px;
  color: var(--color-text-secondary);
}

.tones-table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.icon-btn {
  background: transparent;
  border: 0.5px solid var(--color-border);
  color: var(--color-text-primary);
  border-radius: 4px;
  padding: 2px 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-btn.danger {
  color: #ff5555;
  border-color: rgba(255, 85, 85, 0.3);
}

.tones-table {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.table-head {
  display: grid;
  grid-template-columns: 1fr 1fr 30px;
  gap: 8px;
  font-size: 10px;
  color: var(--color-text-tertiary);
  font-weight: 600;
}

.table-row {
  display: grid;
  grid-template-columns: 1fr 1fr 30px;
  gap: 8px;
  align-items: center;
}

.num-input {
  background: var(--color-bg-elevated);
  border: 0.5px solid var(--color-border);
  color: var(--color-text-primary);
  border-radius: 4px;
  padding: 4px 6px;
  font-size: 11px;
  width: 100%;
}

.param-row {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.param-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.param-label {
  font-size: 11px;
  color: var(--color-text-secondary);
}

.num-input-small {
  background: var(--color-bg-elevated);
  border: 0.5px solid var(--color-border);
  color: var(--color-text-primary);
  border-radius: 4px;
  padding: 2px 4px;
  font-size: 11px;
  width: 60px;
  text-align: right;
}

.slider-param {
  accent-color: var(--color-accent);
  height: 4px;
  cursor: pointer;
}

/* Settings col */
.settings-col {
  width: 160px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.setting-group {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.setting-label {
  font-size: 11px;
  color: var(--color-text-secondary);
}

.actions-row {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-top: auto;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: var(--border-radius-md);
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  border: none;
}

.btn-primary {
  background: var(--color-accent);
  color: #000;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background: var(--color-bg-secondary);
  border: 0.5px solid var(--color-border);
  color: var(--color-text-primary);
}

.error-banner {
  margin-top: 8px;
  padding: 6px 10px;
  background: rgba(255, 85, 85, 0.15);
  border: 0.5px solid #ff5555;
  color: #ff5555;
  font-size: 11px;
  border-radius: 4px;
}

/* Plots */
.plots-area-drawer {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  padding-top: 12px;
}

.plot-wrapper {
  background: var(--color-bg-secondary);
  border-radius: var(--border-radius-md);
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.plot-title {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--color-text-tertiary);
}

.empty-plot {
  height: 130px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-tertiary);
  font-size: 11px;
}
</style>
