<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import { computed, watch } from 'vue';
import { IconPlayerPlay, IconPlayerStop } from '@tabler/icons-vue';
import { useAudioStore } from '../../stores/useAudioStore';
import { useSignalStore } from '../../stores/useSignalStore';
import SpectrumPlot from '../../components/plots/SpectrumPlot.vue';
import type { FftSize, WindowType, AvgMode } from '../../stores/useAudioStore';

const { t } = useI18n();
const audioStore = useAudioStore();
const signalStore = useSignalStore();

const fftSizes: FftSize[] = [1024, 2048, 4096];
const windowTypes: { value: WindowType; label: string }[] = [
  { value: 'hann', label: 'Hann' },
  { value: 'hamming', label: 'Hamming' },
  { value: 'blackman', label: 'Blackman' },
  { value: 'rectangular', label: 'Rectangular' },
];
const avgModes: { value: AvgMode; label: string }[] = [
  { value: 'off', label: 'Off' },
  { value: 8, label: '8' },
  { value: 16, label: '16' },
];

const frequencies = computed(() => signalStore.fftResult.frequencies);
const magnitudes = computed(() => signalStore.fftResult.magnitudes);
const sampleRateLabel = computed(() => {
  const sr = audioStore.sampleRate;
  return sr >= 1000 ? `${sr / 1000} kHz` : `${sr} Hz`;
});

function setFftSize(size: FftSize) {
  if (audioStore.isStreaming) audioStore.stopStream();
  audioStore.fftSize = size;
  if (audioStore.isStreaming) audioStore.startStream();
}

function setWindow(w: WindowType) {
  audioStore.windowType = w;
}

function setAvg(a: AvgMode) {
  audioStore.avgMode = a;
}

// Reactivity: cuando cambia fftSize con stream activo → se reinicia solo por setFftSize
watch(() => audioStore.fftSize, () => {
  // El cambio ya se maneja en setFftSize
});
</script>

<template>
  <div class="rta-view">
    <!-- TopBar -->
    <div class="rta-topbar">
      <span class="rta-title">{{ t('sidebar.rta') }}</span>
      <div class="rta-status">
        <div class="status-dot" :class="{ active: audioStore.isStreaming }"></div>
        <span class="status-label">{{ audioStore.isStreaming ? t('status.streaming') : t('status.ready') }}</span>
      </div>
      <span class="sample-rate-badge">{{ sampleRateLabel }}</span>
    </div>

    <!-- Spectrum Plot -->
    <div class="plot-area">
      <SpectrumPlot
        id="rta-spectrum-plot"
        :frequencies="frequencies"
        :magnitudes="magnitudes"
        :db-scale="true"
        :log-frequency="true"
        :height="0"
        class="spectrum-fill"
      />
      <div v-if="frequencies.length === 0" class="empty-state">
        <span>{{ t('status.ready') }} — {{ t('controls.start') }}</span>
      </div>
    </div>

    <!-- Controls -->
    <div class="controls-bar">
      <div class="control-group">
        <button
          id="rta-start-btn"
          class="btn btn-primary"
          :disabled="audioStore.isStreaming"
          @click="audioStore.startStream()"
        >
          <IconPlayerPlay size="14" />
          {{ t('controls.start') }}
        </button>
        <button
          v-if="!audioStore.isStreaming"
          id="rta-sim-btn"
          class="btn btn-sim"
          @click="audioStore.startSimulation()"
          title="Simular espectro sin usar hardware"
        >
          <IconPlayerPlay size="14" />
          <span>Simular</span>
        </button>
        <button
          id="rta-stop-btn"
          class="btn btn-secondary"
          :disabled="!audioStore.isStreaming"
          @click="audioStore.stopStream()"
        >
          <IconPlayerStop size="14" />
          {{ t('controls.stop') }}
        </button>
      </div>

      <div class="control-group">
        <span class="ctrl-label">FFT:</span>
        <button
          v-for="size in fftSizes"
          :key="size"
          class="pill-btn"
          :class="{ active: audioStore.fftSize === size }"
          @click="setFftSize(size)"
        >{{ size }}</button>
      </div>

      <div class="control-group">
        <span class="ctrl-label">{{ t('controls.window') }}:</span>
        <select
          id="rta-window-select"
          class="select-ctrl"
          :value="audioStore.windowType"
          @change="setWindow(($event.target as HTMLSelectElement).value as WindowType)"
        >
          <option v-for="w in windowTypes" :key="w.value" :value="w.value">{{ w.label }}</option>
        </select>
      </div>

      <div class="control-group">
        <span class="ctrl-label">Avg:</span>
        <button
          v-for="a in avgModes"
          :key="String(a.value)"
          class="pill-btn"
          :class="{ active: audioStore.avgMode === a.value }"
          @click="setAvg(a.value)"
        >{{ a.label }}</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.rta-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  overflow: hidden;
}

/* TopBar */
.rta-topbar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 20px;
  border-bottom: 0.5px solid var(--color-border);
  flex-shrink: 0;
}

.rta-title {
  font-size: 13px;
  font-weight: 600;
}

.rta-status {
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--color-text-tertiary);
  transition: background 0.2s;
}

.status-dot.active {
  background: #22C55E;
  box-shadow: 0 0 6px rgba(34, 197, 94, 0.6);
}

.status-label {
  font-size: 12px;
  color: var(--color-text-secondary);
}

.sample-rate-badge {
  margin-left: auto;
  font-size: 11px;
  font-family: var(--font-mono);
  color: var(--color-text-secondary);
  background: var(--color-bg-elevated);
  padding: 2px 8px;
  border-radius: 10px;
}

/* Plot */
.plot-area {
  flex: 1;
  position: relative;
  overflow: hidden;
  padding: 12px 16px;
}

.spectrum-fill {
  height: 100% !important;
}

/* Override spectrum container height inside flex */
.plot-area :deep(.spectrum-container) {
  height: 100% !important;
}

.empty-state {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: var(--color-text-tertiary);
  pointer-events: none;
}

/* Controls bar */
.controls-bar {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 10px 20px;
  border-top: 0.5px solid var(--color-border);
  flex-shrink: 0;
  flex-wrap: wrap;
}

.control-group {
  display: flex;
  align-items: center;
  gap: 6px;
}

.ctrl-label {
  font-size: 11px;
  color: var(--color-text-secondary);
  font-weight: 500;
}

.btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: var(--border-radius-md);
  font-size: 12px;
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition: opacity 0.15s, background 0.15s;
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

.btn-secondary:not(:disabled):hover {
  background: var(--color-bg-secondary);
}

.pill-btn {
  padding: 4px 10px;
  border-radius: 20px;
  border: 0.5px solid var(--color-border);
  background: var(--color-bg-secondary);
  color: var(--color-text-secondary);
  font-size: 11px;
  font-family: var(--font-mono);
  cursor: pointer;
  transition: background 0.12s, color 0.12s, border-color 0.12s;
}

.pill-btn.active {
  background: var(--color-accent-dim, rgba(0, 217, 126, 0.12));
  color: var(--color-accent);
  border-color: var(--color-accent);
}

.select-ctrl {
  background: var(--color-bg-secondary);
  border: 0.5px solid var(--color-border);
  border-radius: var(--border-radius-md);
  color: var(--color-text-primary);
  font-size: 11px;
  padding: 4px 8px;
  cursor: pointer;
}

.btn-sim {
  background: rgba(129, 140, 248, 0.1);
  color: #a5b4fc;
  border: 0.5px dashed rgba(129, 140, 248, 0.4);
}

.btn-sim:hover {
  background: rgba(129, 140, 248, 0.18);
  border-color: #818cf8;
  color: #c7d2fe;
}
</style>
