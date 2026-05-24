<script setup lang="ts">
import { watch, computed } from 'vue';
import { IconUpload } from '@tabler/icons-vue';
import { useFilterStore } from '../../../stores/useFilterStore';
import FrequencyResponsePlot from '../../plots/FrequencyResponsePlot.vue';

const filterStore = useFilterStore();

const filterTypes = [
  { value: 'moving-average' as const, label: 'Moving Average', eq: 'h[n] = 1/M, 0 ≤ n < M' },
  { value: 'comb' as const,           label: 'Comb Filter',    eq: 'H(z) = b₀ + b₁z⁻¹ + b₂z⁻²' },
  { value: 'fir' as const,            label: 'FIR',            eq: 'H(z) = Σ h[k] z⁻ᵏ' },
];

const passesOptions = [1, 2, 3];

const hasResult = computed(() => filterStore.frequencies.length > 0);

let _debounceTimer: ReturnType<typeof setTimeout> | null = null;

function debouncedCompute() {
  if (_debounceTimer) clearTimeout(_debounceTimer);
  _debounceTimer = setTimeout(() => {
    filterStore.computeResponse();
  }, 200);
}

// Recalcular al cambiar tipo
watch(() => filterStore.filterType, () => {
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
  try {
    const coeffs = text.trim().split(/[\s,;]+/).map(Number).filter(v => !isNaN(v));
    filterStore.firCoefficients = coeffs;
  } catch {
    // ignore parse errors
  }
}
</script>

<template>
  <div class="fd-panel">
    <!-- Filter type selector -->
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

    <!-- Parameters panel -->
    <div class="params-panel">
      <!-- Moving Average -->
      <template v-if="filterStore.filterType === 'moving-average'">
        <div class="param-row">
          <label class="param-label" for="ma-m-slider">M = {{ filterStore.maM }}</label>
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
          <span class="param-label">Passes:</span>
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
        <div class="param-eq">H(z) = {{ filterStore.combB0 }} + {{ filterStore.combB1 }}z⁻¹ + {{ filterStore.combB2 }}z⁻²</div>
      </template>

      <!-- FIR -->
      <template v-else>
        <div class="param-row">
          <span class="param-label">Coefficients file (.txt / .csv):</span>
          <label class="upload-btn" for="fir-file-input">
            <IconUpload size="12" />
            <span>{{ filterStore.firCoefficients.length > 0 ? `${filterStore.firCoefficients.length} coeffs loaded` : 'Upload' }}</span>
            <input id="fir-file-input" type="file" accept=".txt,.csv" class="file-input" @change="onFirFile" />
          </label>
        </div>
        <div v-if="filterStore.firCoefficients.length > 0" class="param-eq">
          h[n] = [{{ filterStore.firCoefficients.slice(0, 6).join(', ') }}{{ filterStore.firCoefficients.length > 6 ? ', …' : '' }}]
        </div>
      </template>

      <!-- Loading/error -->
      <div v-if="filterStore.isLoading" class="status-text">Computing…</div>
      <div v-if="filterStore.error" class="error-text">{{ filterStore.error }}</div>
    </div>

    <!-- FrequencyResponse Plot -->
    <div class="plots-area-drawer">
      <div class="plot-wrapper">
        <FrequencyResponsePlot
          v-if="hasResult"
          id="fd-fr-plot"
          :frequencies="filterStore.frequencies"
          :magnitud-db="filterStore.magnitudeDb"
          :phase-rad="filterStore.phaseRad"
          :height="240"
        />
        <div v-else class="empty-plot">
          Ajustá los parámetros para calcular h[n]
        </div>
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

/* Type selector */
.type-selector {
  display: flex;
  gap: 8px;
  padding-bottom: 12px;
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

/* Params panel */
.params-panel {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px;
  background: var(--color-bg-secondary);
  border: 0.5px solid var(--color-border);
  border-radius: var(--border-radius-md);
}

.param-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.param-label {
  font-size: 11px;
  color: var(--color-text-secondary);
  font-weight: 500;
  min-width: 80px;
  flex-shrink: 0;
}

.slider {
  flex: 1;
  accent-color: var(--color-accent);
  cursor: pointer;
}

.num-input {
  width: 80px;
  padding: 3px 6px;
  background: var(--color-bg-elevated);
  border: 0.5px solid var(--color-border);
  border-radius: var(--border-radius-md);
  color: var(--color-text-primary);
  font-size: 11px;
  font-family: var(--font-mono);
}

.pill-group {
  display: flex;
  gap: 6px;
}

.pill-btn {
  padding: 3px 10px;
  border-radius: 12px;
  border: 0.5px solid var(--color-border);
  background: var(--color-bg-elevated);
  color: var(--color-text-secondary);
  font-size: 10px;
  cursor: pointer;
  transition: background 0.12s, color 0.12s, border-color 0.12s;
}

.pill-btn.active {
  background: var(--color-accent-dim);
  color: var(--color-accent);
  border-color: var(--color-accent);
}

.param-eq {
  font-size: 10px;
  font-family: var(--font-mono);
  color: var(--color-text-secondary);
  padding: 4px 8px;
  background: var(--color-bg-elevated);
  border-radius: var(--border-radius-md);
}

.upload-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: var(--border-radius-md);
  border: 0.5px solid var(--color-border);
  background: var(--color-bg-elevated);
  font-size: 11px;
  color: var(--color-text-secondary);
  cursor: pointer;
  position: relative;
}

.file-input {
  position: absolute;
  inset: 0;
  opacity: 0;
  cursor: pointer;
  width: 100%;
  height: 100%;
}

.status-text {
  font-size: 11px;
  color: var(--color-text-secondary);
}

.error-text {
  font-size: 11px;
  color: #EF4444;
}

/* Plots */
.plots-area-drawer {
  margin-top: 16px;
}

.empty-plot {
  height: 240px;
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
