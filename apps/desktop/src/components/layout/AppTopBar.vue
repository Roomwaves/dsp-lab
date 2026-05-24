<script setup lang="ts">
import { ref } from 'vue';
import { useMeasurementSession } from '../../stores/useMeasurementSession';
import { IconCamera, IconActivity } from '@tabler/icons-vue';

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
      <IconActivity size="18" class="logo" />
      <span class="title">DSP Analyzer <span class="version">v0.1.0</span></span>
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
.app-topbar {
  height: 48px;
  border-bottom: 1px solid var(--color-border-tertiary);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  flex-shrink: 0;
  background: var(--color-bg-primary);
}

.brand {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 240px; /* match sidebar width roughly for alignment */
}

.logo {
  color: var(--color-accent);
}

.title {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.version {
  font-size: 11px;
  color: var(--color-text-secondary);
  font-weight: normal;
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
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.live {
  color: var(--color-accent);
}

.live .status-dot {
  background: var(--color-accent);
  box-shadow: 0 0 8px var(--color-accent);
}

.no-signal {
  color: var(--color-text-tertiary);
}

.no-signal .status-dot {
  border: 2px solid var(--color-text-tertiary);
  background: transparent;
}

.computing {
  color: #F59E0B;
}

.computing .status-dot {
  border: 2px solid #F59E0B;
  border-top-color: transparent;
  background: transparent;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.actions {
  display: flex;
  justify-content: flex-end;
  width: 240px;
}

.capture-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 4px;
  background: var(--color-bg-tertiary);
  border: 1px solid var(--color-border-tertiary);
  color: var(--color-text-primary);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.capture-btn:not(:disabled):hover {
  background: var(--color-bg-hover);
  border-color: var(--color-border-secondary);
}

.capture-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.capture-btn.flash {
  opacity: 0.3;
}
</style>
