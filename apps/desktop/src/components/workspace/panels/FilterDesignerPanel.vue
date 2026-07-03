<script setup lang="ts">
import { watch, computed, ref, onMounted } from 'vue';
import { IconUpload, IconScissors } from '@tabler/icons-vue';
import { useFilterStore } from '../../../stores/useFilterStore';
import FrequencyResponsePlot from '../../plots/FrequencyResponsePlot.vue';
import WaveformPlot from '../../plots/WaveformPlot.vue';

const filterStore = useFilterStore();

const filterTypes = [
  { value: 'moving-average' as const, label: 'Moving Average', eq: 'h[n] = 1/M, 0 ≤ n < M' },
  { value: 'comb' as const,           label: 'Comb Filter',    eq: 'H(z) = b₀ + b₁z⁻¹ + b₂z⁻²' },
  { value: 'fir' as const,            label: 'FIR',            eq: 'H(z) = Σ h[k] z⁻ᵏ' },
];

const passesOptions = [1, 2, 3];
const fsOptions = [8000, 22050, 44100, 48000, 96000];
const truncateN = ref(8);

const hasResult = computed(() => filterStore.frequencies.length > 0);

let _debounceTimer: ReturnType<typeof setTimeout> | null = null;

function debouncedCompute() {
  if (_debounceTimer) clearTimeout(_debounceTimer);
  _debounceTimer = setTimeout(() => {
    filterStore.computeResponse();
  }, 200);
}

onMounted(() => {
  if (!hasResult.value) {
    filterStore.computeResponse();
  }
});

// Recalcular al cambiar tipo o fs
watch([() => filterStore.filterType, () => filterStore.fs], () => {
  filterStore.computeResponse();
});

// Recalcular al cambiar params con debounce
watch(
  [() => filterStore.maM, () => filterStore.maPasses,
   () => filterStore.combB0, () => filterStore.combB1, () => filterStore.combB2,
   () => filterStore.firCoefficients],
  debouncedCompute,
);

async function onFirFile(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0];
  if (!file) return;
  const text = await file.text();
  filterStore.parseFirText(text);
  filterStore.computeResponse();
}

function onFirTextInput(e: Event) {
  const text = (e.target as HTMLInputElement).value;
  filterStore.parseFirText(text);
}

function handleTruncate() {
  if (truncateN.value > 0) {
    filterStore.truncateFir(truncateN.value);
  }
}
</script>

<template>
  <div class="fd-panel">
    <!-- Filter type selector & Fs selector -->
    <div class="top-controls">
      <div class="type-selector">
        <button
          v-for="ft in filterTypes"
          :key="ft.value"
          class="type-btn"
          :class="{ active: filterStore.filterType === ft.value }"
          @click="filterStore.filterType = ft.value"
        >
          {{ ft.label }}
        </button>
      </div>

      <div class="fs-selector">
        <label for="fd-fs-select" class="fs-label">Fs:</label>
        <select id="fd-fs-select" v-model.number="filterStore.fs" class="select-ctrl">
          <option v-for="f in fsOptions" :key="f" :value="f">{{ f >= 1000 ? f / 1000 + ' kHz' : f + ' Hz' }}</option>
        </select>
      </div>
    </div>

    <!-- Parameters panel -->
    <div class="params-panel">
      <!-- Moving Average -->
      <template v-if="filterStore.filterType === 'moving-average'">
        <div class="param-row">
          <label class="param-label" for="ma-m-slider">M = {{ filterStore.maM }} muestras</label>
          <input
            id="ma-m-slider"
            v-model.number="filterStore.maM"
            type="range"
            min="2"
            max="64"
            step="1"
            class="slider"
          />
        </div>
        <div class="param-row">
          <span class="param-label">Pasadas (Passes):</span>
          <div class="pill-group">
            <button
              v-for="p in passesOptions"
              :key="p"
              class="pill-btn"
              :class="{ active: filterStore.maPasses === p }"
              @click="filterStore.maPasses = p"
            >{{ p }}</button>
          </div>
        </div>
        <div class="param-eq">h[n] = 1/{{ filterStore.maM }}, 0 ≤ n &lt; {{ filterStore.maM }} (×{{ filterStore.maPasses }})</div>
      </template>

      <!-- Comb Filter -->
      <template v-else-if="filterStore.filterType === 'comb'">
        <div class="comb-inputs">
          <div class="param-row">
            <label class="param-label" for="comb-b0">b₀</label>
            <input id="comb-b0" v-model.number="filterStore.combB0" type="number" step="0.01" class="num-input" />
          </div>
          <div class="param-row">
            <label class="param-label" for="comb-b1">b₁</label>
            <input id="comb-b1" v-model.number="filterStore.combB1" type="number" step="0.01" class="num-input" />
          </div>
          <div class="param-row">
            <label class="param-label" for="comb-b2">b₂</label>
            <input id="comb-b2" v-model.number="filterStore.combB2" type="number" step="0.01" class="num-input" />
          </div>
        </div>
        <div class="param-eq">H(z) = {{ filterStore.combB0 }} + {{ filterStore.combB1 }}z⁻¹ + {{ filterStore.combB2 }}z⁻²</div>
      </template>

      <!-- FIR -->
      <template v-else>
        <div class="fir-container">
          <div class="param-row">
            <label class="param-label">Coeficientes h[n] (separados por coma o espacio):</label>
            <input
              type="text"
              :value="filterStore.firText"
              class="text-input"
              placeholder="1, 0.5, 0.25, 0.125"
              @input="onFirTextInput"
            />
          </div>

          <div class="fir-actions">
            <label class="upload-btn" for="fir-file-input">
              <IconUpload size="12" />
              <span>{{ filterStore.firCoefficients.length > 0 ? `${filterStore.firCoefficients.length} coefs cargados` : 'Cargar Archivo' }}</span>
              <input id="fir-file-input" type="file" accept=".txt,.csv" class="file-input" @change="onFirFile" />
            </label>

            <div class="truncate-box" v-if="filterStore.firCoefficients.length > 1">
              <span class="param-label">Truncar N:</span>
              <input v-model.number="truncateN" type="number" min="1" :max="filterStore.firCoefficients.length" class="num-input-small" />
              <button class="btn-utility" @click="handleTruncate">
                <IconScissors size="12" />
                Truncar
              </button>
            </div>
          </div>
        </div>
        <div v-if="filterStore.firCoefficients.length > 0" class="param-eq">
          h[n] = [{{ filterStore.firCoefficients.slice(0, 8).join(', ') }}{{ filterStore.firCoefficients.length > 8 ? ', …' : '' }}] ({{ filterStore.firCoefficients.length }} coefs)
        </div>
      </template>

      <!-- Loading/error -->
      <div v-if="filterStore.isLoading" class="status-text">Calculando respuesta…</div>
      <div v-if="filterStore.error" class="error-text">{{ filterStore.error }}</div>
    </div>

    <!-- Plots (Frequency Response & Impulse Response) -->
    <div class="plots-area-drawer">
      <div class="plot-wrapper">
        <div class="plot-header-title">Respuesta en Frecuencia H(ω)</div>
        <FrequencyResponsePlot
          v-if="hasResult"
          id="fd-fr-plot"
          :frequencies="filterStore.frequencies"
          :magnitud-db="filterStore.magnitudeDb"
          :phase-rad="filterStore.phaseRad"
          :height="200"
        />
        <div v-else class="empty-plot">Calculando respuesta…</div>
      </div>

      <div class="plot-wrapper">
        <div class="plot-header-title">Respuesta al Impulso h[n]</div>
        <WaveformPlot
          v-if="filterStore.impulseSamples.length > 0"
          id="fd-ir-plot"
          :samples="filterStore.impulseSamples"
          :fs="filterStore.fs"
          :height="200"
        />
        <div v-else class="empty-plot">—</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.fd-panel {
  display: flex;
  flex-direction: column;
  width: 100%;
}

.top-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding-bottom: 12px;
}

/* Type selector */
.type-selector {
  display: flex;
  gap: 8px;
  flex: 1;
}

.type-btn {
  flex: 1;
  padding: 6px 10px;
  border-radius: var(--border-radius-md);
  border: 0.5px solid var(--color-border);
  background: var(--color-bg-secondary);
  color: var(--color-text-secondary);
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  text-align: center;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  transition: background 0.12s, color 0.12s, border-color 0.12s;
}

.type-btn:hover {
  background: var(--color-bg-elevated);
}

.type-btn.active {
  background: var(--color-accent-dim);
  color: var(--color-accent);
  border-color: var(--color-accent);
}

.fs-selector {
  display: flex;
  align-items: center;
  gap: 6px;
}

.fs-label {
  font-size: 11px;
  color: var(--color-text-secondary);
  font-weight: 600;
}

.select-ctrl {
  background: var(--surface-3, #1e1e21);
  border: 0.5px solid var(--color-border);
  color: var(--text-white, #ffffff);
  border-radius: var(--border-radius-md);
  padding: 4px 8px;
  font-size: 11px;
  outline: none;
  cursor: pointer;
}

.select-ctrl option {
  background: var(--surface-3, #1e1e21);
  color: var(--text-white, #ffffff);
}

/* Params panel */
.params-panel {
  display: flex;
  flex-direction: column;
  gap: 10px;
  background: var(--color-bg-secondary);
  border-radius: var(--border-radius-md);
  padding: 12px;
}

.comb-inputs {
  display: flex;
  gap: 16px;
}

.param-row {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.param-label {
  font-size: 11px;
  color: var(--color-text-secondary);
}

.slider {
  accent-color: var(--color-accent);
  height: 4px;
  cursor: pointer;
}

.pill-group {
  display: flex;
  gap: 6px;
}

.pill-btn {
  padding: 4px 12px;
  border-radius: var(--radius-pill);
  border: 0.5px solid var(--color-border);
  background: var(--color-bg-elevated);
  color: var(--color-text-secondary);
  font-size: 11px;
  cursor: pointer;
}

.pill-btn.active {
  background: var(--color-accent-dim);
  color: var(--color-accent);
  border-color: var(--color-accent);
}

.num-input {
  background: var(--color-bg-elevated);
  border: 0.5px solid var(--color-border);
  color: var(--color-text-primary);
  border-radius: 4px;
  padding: 4px 8px;
  font-size: 11px;
  width: 90px;
}

.num-input-small {
  background: var(--color-bg-elevated);
  border: 0.5px solid var(--color-border);
  color: var(--color-text-primary);
  border-radius: 4px;
  padding: 3px 6px;
  font-size: 11px;
  width: 50px;
  text-align: center;
}

.text-input {
  background: var(--color-bg-elevated);
  border: 0.5px solid var(--color-border);
  color: var(--color-text-primary);
  border-radius: 4px;
  padding: 6px 10px;
  font-size: 11px;
  font-family: var(--font-mono);
  width: 100%;
}

.fir-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.fir-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.upload-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 4px;
  border: 0.5px solid var(--color-border);
  background: var(--color-bg-elevated);
  color: var(--color-text-primary);
  font-size: 11px;
  cursor: pointer;
}

.file-input {
  display: none;
}

.truncate-box {
  display: flex;
  align-items: center;
  gap: 8px;
}

.param-eq {
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--color-text-tertiary);
}

.status-text {
  font-size: 11px;
  color: var(--color-accent);
}

.error-text {
  font-size: 11px;
  color: #ff5555;
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

.plot-header-title {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--color-text-tertiary);
}

.empty-plot {
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-tertiary);
  font-size: 11px;
}
</style>
