<script setup lang="ts">
import { computed } from 'vue';
import { useMeasurementSession } from '../../../stores/useMeasurementSession';
import WaveformPlot from '../../plots/WaveformPlot.vue';

const session = useMeasurementSession();

const traces = computed(() => {
  const list = [];
  if (session.x && session.x.samples && session.x.samples.length > 0) {
    list.push({
      samples: session.x.samples,
      fs: session.x.fs,
      color: '#00D97E',
      label: 'Referencia (X)'
    });
  }
  if (session.y && session.y.samples && session.y.samples.length > 0) {
    list.push({
      samples: session.y.samples,
      fs: session.y.fs,
      color: '#3B82F6',
      label: 'Medición (Y)'
    });
  }
  return list;
});
</script>

<template>
  <div class="panel-inner">
    <div v-if="!session.x && !session.y" class="empty-state">
      <div class="placeholder">Cargá señales X e Y para</div>
      <div class="placeholder-sub">ver la forma de onda.</div>
    </div>
    <div v-else class="plot-container">
      <div class="legend">
        <div class="legend-item" v-if="session.x"><span class="legend-dot ref"></span>Referencia (X)</div>
        <div class="legend-item" v-if="session.y"><span class="legend-dot meas"></span>Medición (Y)</div>
      </div>
      <WaveformPlot
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
