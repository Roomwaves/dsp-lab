<script setup lang="ts">
import { computed } from 'vue';
import { useAppStore } from '../../stores/useAppStore';
import { useAudioStore } from '../../stores/useAudioStore';
import { storeToRefs } from 'pinia';
import WorkspacePanel from './WorkspacePanel.vue';
import MagnitudePanel from './panels/MagnitudePanel.vue';
import PhasePanel from './panels/PhasePanel.vue';
import CoherencePanel from './panels/CoherencePanel.vue';
import RTAPanel from './panels/RTAPanel.vue';
import WaveformPanel from './panels/WaveformPanel.vue';
import IOSetup from './IOSetup.vue';
import { IconPlayerStop } from '@tabler/icons-vue';

const appStore = useAppStore();
const audioStore = useAudioStore();

const {
  selectedInputDevice,
  selectedSampleRate,
  selectedBufferSize,
  estimatedLatencyMs,
  levelX_dBFS,
  levelY_dBFS
} = storeToRefs(audioStore);

const allPanelsHidden = computed(() => {
  return !appStore.panelVisibility.magnitude &&
         !appStore.panelVisibility.phase &&
         !appStore.panelVisibility.coherence &&
         !appStore.panelVisibility.rta &&
         !appStore.panelVisibility.waveform;
});

const meterWidthX = computed(() => {
  const lvl = levelX_dBFS.value;
  if (lvl === -Infinity || isNaN(lvl)) return 0;
  return Math.max(0, Math.min(100, ((lvl - (-60)) / 60) * 100));
});

const meterWidthY = computed(() => {
  const lvl = levelY_dBFS.value;
  if (lvl === -Infinity || isNaN(lvl)) return 0;
  return Math.max(0, Math.min(100, ((lvl - (-60)) / 60) * 100));
});

function formatDbfs(val: number) {
  if (val === -Infinity || isNaN(val) || val <= -99) return '-inf';
  return val.toFixed(1) + ' dB';
}
</script>

<template>
  <div class="workspace-container">
    <template v-if="audioStore.streamState !== 'running'">
      <IOSetup />
    </template>

    <template v-else>
      <!-- Dashboard superior en vivo -->
      <div class="stream-dashboard-bar">
        <div class="config-summary">
          <span class="active-dot"></span>
          <span class="device-name" :title="selectedInputDevice?.name">
            {{ selectedInputDevice?.name }}
          </span>
          <span class="divider">·</span>
          <span class="meta-item">{{ selectedSampleRate / 1000 }} kHz</span>
          <span class="divider">·</span>
          <span class="meta-item">Buf: {{ selectedBufferSize }}</span>
          <span class="divider">·</span>
          <span class="meta-item">{{ estimatedLatencyMs.toFixed(1) }} ms</span>
        </div>

        <div class="meters-container">
          <!-- Canal X (Referencia) -->
          <div class="meter-wrapper">
            <span class="meter-label">Ref X</span>
            <div class="meter-bg">
              <div class="meter-fill fill-x" :style="{ width: meterWidthX + '%' }"></div>
            </div>
            <span class="meter-value" :class="{ 'inf': levelX_dBFS <= -60 }">
              {{ formatDbfs(levelX_dBFS) }}
            </span>
          </div>

          <!-- Canal Y (Medición) -->
          <div class="meter-wrapper">
            <span class="meter-label">Mic Y</span>
            <div class="meter-bg">
              <div class="meter-fill fill-y" :style="{ width: meterWidthY + '%' }"></div>
            </div>
            <span class="meter-value" :class="{ 'inf': levelY_dBFS <= -60 }">
              {{ formatDbfs(levelY_dBFS) }}
            </span>
          </div>
        </div>

        <button @click="audioStore.stopStream" class="btn-stop-stream" title="Detener captura de audio">
          <IconPlayerStop size="14" class="stop-icon" />
          <span>Detener</span>
        </button>
      </div>

      <!-- Contenedor scrollable de paneles -->
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
  </div>
</template>

<style scoped>
.workspace-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 0;
  background-color: var(--color-bg-primary);
}

.stream-dashboard-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 20px;
  background: rgba(24, 28, 36, 0.75);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border-bottom: 1px solid var(--color-border);
  height: 52px;
  flex-shrink: 0;
  gap: 24px;
  z-index: 2;
}

.config-summary {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 11px;
  color: var(--color-text-secondary);
}

.active-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background-color: var(--color-accent);
  box-shadow: 0 0 8px var(--color-accent);
  animation: blink 1.5s infinite alternate;
}

.device-name {
  font-weight: 500;
  color: var(--color-text-primary);
  max-width: 160px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.divider {
  opacity: 0.3;
}

.meta-item {
  font-family: var(--font-mono);
}

.meters-container {
  display: flex;
  align-items: center;
  gap: 20px;
  flex: 1;
  max-width: 500px;
}

.meter-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.meter-label {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--color-text-secondary);
  width: 32px;
  letter-spacing: 0.5px;
}

.meter-bg {
  height: 8px;
  background: rgba(10, 11, 13, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.02);
  border-radius: 4px;
  flex: 1;
  overflow: hidden;
  position: relative;
}

.meter-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.1s cubic-bezier(0.1, 0.8, 0.3, 1);
}

.fill-x {
  background: linear-gradient(to right, #00d97e 75%, #f59e0b 90%, #ef4444 100%);
}

.fill-y {
  background: linear-gradient(to right, #818cf8 75%, #ec4899 90%, #ef4444 100%);
}

.meter-value {
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--color-text-primary);
  width: 52px;
  text-align: right;
}

.meter-value.inf {
  color: var(--color-text-secondary);
  opacity: 0.5;
}

.btn-stop-stream {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: rgba(239, 68, 68, 0.08);
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: var(--border-radius-md);
  color: #f87171;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-stop-stream:hover {
  background: #ef4444;
  color: #050505;
  border-color: transparent;
  box-shadow: 0 0 10px rgba(239, 68, 68, 0.3);
}

.btn-stop-stream:active {
  transform: scale(0.97);
}

.stop-icon {
  flex-shrink: 0;
}

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

@keyframes blink {
  0% { opacity: 0.4; }
  100% { opacity: 1; }
}
</style>
