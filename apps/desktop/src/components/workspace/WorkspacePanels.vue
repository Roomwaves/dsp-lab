<script setup lang="ts">
import { computed } from 'vue';
import { useAppStore } from '../../stores/useAppStore';
import WorkspacePanel from './WorkspacePanel.vue';
import MagnitudePanel from './panels/MagnitudePanel.vue';
import PhasePanel from './panels/PhasePanel.vue';
import CoherencePanel from './panels/CoherencePanel.vue';
import RTAPanel from './panels/RTAPanel.vue';
import WaveformPanel from './panels/WaveformPanel.vue';

const appStore = useAppStore();

const allPanelsHidden = computed(() => {
  return !appStore.panelVisibility.magnitude &&
         !appStore.panelVisibility.phase &&
         !appStore.panelVisibility.coherence &&
         !appStore.panelVisibility.rta &&
         !appStore.panelVisibility.waveform;
});
</script>

<template>
  <div class="workspace-panels">
    <WorkspacePanel
      title="Magnitud H(ω)"
      :visible="appStore.panelVisibility.magnitude"
      @toggle="appStore.togglePanelVisibility('magnitude')"
    >
      <MagnitudePanel />
    </WorkspacePanel>

    <WorkspacePanel
      title="Fase"
      :visible="appStore.panelVisibility.phase"
      @toggle="appStore.togglePanelVisibility('phase')"
    >
      <PhasePanel />
    </WorkspacePanel>

    <WorkspacePanel
      title="Coherencia γ²"
      :visible="appStore.panelVisibility.coherence"
      @toggle="appStore.togglePanelVisibility('coherence')"
    >
      <CoherencePanel />
    </WorkspacePanel>

    <WorkspacePanel
      title="RTA (X e Y superpuestas)"
      :visible="appStore.panelVisibility.rta"
      @toggle="appStore.togglePanelVisibility('rta')"
    >
      <RTAPanel />
    </WorkspacePanel>

    <WorkspacePanel
      title="Forma de onda"
      :visible="appStore.panelVisibility.waveform"
      @toggle="appStore.togglePanelVisibility('waveform')"
    >
      <WaveformPanel />
    </WorkspacePanel>

    <div v-if="allPanelsHidden" class="empty-panels-state">
      <div class="empty-text">Activá al menos un panel</div>
    </div>
  </div>
</template>

<style scoped>
.workspace-panels {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  min-height: 0;
}
.empty-panels-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  background: var(--color-bg-secondary);
}
.empty-text {
  font-size: 13px;
  color: var(--color-text-secondary);
  font-family: var(--font-mono);
  background: var(--color-bg-elevated);
  padding: 8px 16px;
  border-radius: var(--border-radius-md);
  border: 1px solid var(--color-border);
}
</style>
