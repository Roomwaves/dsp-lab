<script setup lang="ts">
import { computed } from 'vue';
import { useMeasurementSession } from '../../../stores/useMeasurementSession';
import FrequencyResponsePlot from '../../plots/FrequencyResponsePlot.vue';

const session = useMeasurementSession();

const frequencies = computed(() => session.liveResult?.frequencies ?? []);
const magnitude_db = computed(() => session.liveResult?.magnitude_db ?? []);

const snapshotTraces = computed(() =>
  session.visibleSnapshots
    .filter(s => s.data && s.data.frequencies && s.data.magnitude_db)
    .map(s => ({
      frequencies: s.data.frequencies,
      magnitudeDb: s.data.magnitude_db,
      color: s.color,
      label: s.label,
    }))
);
</script>

<template>
  <div class="panel-inner">
    <div v-if="!session.hasLiveResult" class="empty-state">
      <div class="placeholder">Cargá señales X e Y para</div>
      <div class="placeholder-sub">ver la función de transferencia.</div>
    </div>
    <FrequencyResponsePlot
      v-else
      :frequencies="frequencies"
      :magnitud-db="magnitude_db"
      :phase-rad="[]"
      mode="magnitude"
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
