<script setup lang="ts">
import { computed } from 'vue';
import { useMeasurementSession } from '../../../stores/useMeasurementSession';
import FrequencyResponsePlot from '../../plots/FrequencyResponsePlot.vue';

const session = useMeasurementSession();

const frequencies = computed(() => session.liveResult?.frequencies ?? []);
const phase_rad = computed(() => session.liveResult?.phase_rad ?? []);

const snapshotTraces = computed(() =>
  session.visibleSnapshots
    .filter(s => s.data && s.data.frequencies && s.data.phase_rad)
    .map(s => ({
      frequencies: s.data.frequencies,
      phaseRad: s.data.phase_rad,
      color: s.color,
      label: s.label,
    }))
);
</script>

<template>
  <div class="panel-inner">
    <div v-if="!session.hasLiveResult" class="empty-state">
      <div class="placeholder">Cargá señales X e Y para</div>
      <div class="placeholder-sub">ver la fase de la función de transferencia.</div>
    </div>
    <FrequencyResponsePlot
      v-else
      :frequencies="frequencies"
      :magnitud-db="[]"
      :phase-rad="phase_rad"
      mode="phase"
      :traces="snapshotTraces"
      :height="200"
    />
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
</style>
