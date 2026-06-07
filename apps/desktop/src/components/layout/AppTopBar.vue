<script setup lang="ts">
import { ref } from 'vue';
import { useMeasurementSession } from '../../stores/useMeasurementSession';
import { IconCamera } from '@tabler/icons-vue';

const session = useMeasurementSession();
const flash = ref(false);

function onCapture() {
  if (!session.hasLiveResult || session.snapshots.length >= 8) return;
  session.captureSnapshot();
  flash.value = true;
  setTimeout(() => {
    flash.value = false;
  }, 300);
}
</script>

<template>
  <div class="app-topbar">
    <div class="brand">
      <img src="/path190.svg" alt="RoomWaves Icon" class="topbar-logo-img" />
      <span class="title">DSP-LAB <span class="version">v0.1.0</span></span>
    </div>
    
    <div class="status-container">
      <template v-if="session.isComputing">
        <div class="status-indicator computing">
          <div class="status-dot"></div>
          <span class="status-text">○ CALCULANDO</span>
        </div>
      </template>
      <template v-else-if="session.hasLiveResult">
        <div class="status-indicator live">
          <div class="status-dot"></div>
          <span class="status-text">● LIVE</span>
        </div>
      </template>
      <template v-else>
        <div class="status-indicator no-signal">
          <div class="status-dot empty"></div>
          <span class="status-text">○ SIN SEÑAL</span>
        </div>
      </template>
    </div>

    <div class="actions">
      <button 
        class="capture-btn" 
        :class="{ flash }" 
        :disabled="!session.hasLiveResult || session.snapshots.length >= 8"
        :title="session.snapshots.length >= 8 ? 'Máximo 8 capturas. Eliminá una para continuar.' : ''"
        @click="onCapture"
      >
        <IconCamera size="16" />
        Capturar
      </button>
    </div>
  </div>
</template>

<style scoped>
/* DESIGN_GUIDE §3 — Global Site Navigation & Header */
.app-topbar {
  height: 48px;
  border-bottom: 1px solid var(--border-ghost);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  flex-shrink: 0;
  background: var(--surface-1);
}

.brand {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 240px;
}

.topbar-logo-img {
  width: 18px;
  height: auto;

}

.title {
  font-family: var(--font-ui);
  font-size: 13px;
  font-weight: 400;
  color: var(--text-white);
  letter-spacing: 0.02em;
}

.version {
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--text-gray);
  font-weight: 400;
  margin-left: 2px;
}

.status-container {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
}

.live {
  color: var(--accent-lime);
}

.live .status-dot {
  background: var(--accent-lime);
  box-shadow: 0 0 8px var(--accent-lime);
}

.no-signal {
  color: var(--text-gray);
}

.no-signal .status-dot {
  border: 1.5px solid var(--border-default);
  background: transparent;
}

.computing {
  color: var(--accent-peach);
}

.computing .status-dot {
  border: 1.5px solid var(--accent-peach);
  border-top-color: transparent;
  background: transparent;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to   { transform: rotate(360deg); }
}

.actions {
  display: flex;
  justify-content: flex-end;
  width: 240px;
}

/* Utility Tonal Button (DESIGN_GUIDE §5) */
.capture-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 13px;
  border-radius: var(--radius-sm);
  background: var(--surface-2);
  border: 1px solid var(--border-default);
  color: var(--text-silver);
  font-family: var(--font-ui);
  font-size: 13px;
  font-weight: 400;
  cursor: pointer;
  transition: all 0.15s var(--ease-material);
}

.capture-btn:not(:disabled):hover {
  background: var(--surface-3);
  border-color: var(--border-bold);
  color: var(--text-white);
}

.capture-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.capture-btn.flash {
  opacity: 0.3;
}
</style>
