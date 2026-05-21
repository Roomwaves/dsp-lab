<script setup lang="ts">
import { computed } from 'vue';
import { useMeasurementSession } from '../../../stores/useMeasurementSession';
import CoherencePlot from '../../plots/CoherencePlot.vue';

const session = useMeasurementSession();

const frequencies = computed(() => session.liveResult?.frequencies ?? []);
const coherence = computed(() => session.liveResult?.coherence ?? []);

const snapshotTraces = computed(() =>
  session.visibleSnapshots
    .filter(s => s.data && s.data.frequencies && s.data.coherence)
    .map(s => ({
      frequencies: s.data.frequencies,
      coherence: s.data.coherence,
      color: s.color,
      label: s.label,
    }))
);
</script>

<template>
  <div class="panel-inner">
    <div v-if="!session.hasLiveResult" class="empty-state">
      <div class="placeholder">Cargá señales X e Y para</div>
      <div class="placeholder-sub">ver la coherencia.</div>
    </div>
    <CoherencePlot
      v-else
      :frequencies="frequencies"
      :coherence="coherence"
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
