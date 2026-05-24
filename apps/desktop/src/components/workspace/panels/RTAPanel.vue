<script setup lang="ts">
import { computed } from 'vue';
import { useMeasurementSession } from '../../../stores/useMeasurementSession';
import SpectrumPlot from '../../plots/SpectrumPlot.vue';

const session = useMeasurementSession();

const traces = computed(() => {
  const list = [];
  if (session.liveResult && session.liveResult.frequencies && session.liveResult.frequencies.length > 0) {
    if (session.liveResult.spectrum_x) {
      list.push({
        frequencies: session.liveResult.frequencies,
        magnitudes: session.liveResult.spectrum_x,
        color: '#00D97E',
        label: 'Referencia (X)'
      });
    }
    if (session.liveResult.spectrum_y) {
      list.push({
        frequencies: session.liveResult.frequencies,
        magnitudes: session.liveResult.spectrum_y,
        color: '#3B82F6',
        label: 'Medición (Y)'
      });
    }
  }
  
  // Snapshots can also be superimposed
  for (const s of session.visibleSnapshots) {
    if (s.data && s.data.frequencies && s.data.frequencies.length > 0) {
      if (s.data.spectrum_x) {
        list.push({
          frequencies: s.data.frequencies,
          magnitudes: s.data.spectrum_x,
          color: s.color,
          label: `${s.label} (X)`
        });
      }
      if (s.data.spectrum_y) {
        list.push({
          frequencies: s.data.frequencies,
          magnitudes: s.data.spectrum_y,
          color: s.color,
          label: `${s.label} (Y)`
        });
      }
    }
  }
  return list;
});
</script>

<template>
  <div class="panel-inner">
    <div v-if="!session.hasLiveResult" class="empty-state">
      <div class="placeholder">Cargá señales X e Y para</div>
      <div class="placeholder-sub">ver el espectro RTA.</div>
    </div>
    <div v-else class="plot-container">
      <div class="legend">
        <div class="legend-item"><span class="legend-dot ref"></span>Referencia (X)</div>
        <div class="legend-item"><span class="legend-dot meas"></span>Medición (Y)</div>
      </div>
      <SpectrumPlot
        :db-scale="true"
        :log-frequency="true"
        :traces="traces"
        :height="200"
      />
    </div>
  </div>
</template>

<style scoped>
.panel-inner {
  width: 100%;
}
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px 16px;
  background: var(--color-bg-secondary);
  border-radius: var(--border-radius-md);
  border: 1px dashed var(--color-border);
}
.plot-container {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.legend {
  display: flex;
  gap: 12px;
  font-size: 10px;
  color: var(--color-text-secondary);
  justify-content: flex-end;
}
.legend-item {
  display: flex;
  align-items: center;
  gap: 4px;
}
.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}
.legend-dot.ref {
  background: #00D97E;
}
.legend-dot.meas {
  background: #3B82F6;
}
</style>
