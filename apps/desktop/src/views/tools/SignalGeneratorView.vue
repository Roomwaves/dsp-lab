<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import SignalGeneratorPanel from '../../components/workspace/panels/SignalGeneratorPanel.vue';

const { t } = useI18n();
</script>

<template>
  <div class="sg-view">
    <!-- TopBar -->
    <div class="sg-topbar">
      <span class="sg-title">{{ t('sidebar.signal_generator') }}</span>
      <span class="sg-subtitle">Generador de señales de precisión: Seno multitono, Cuadrada, Triangular, Ruido Blanco/Rosa y Barridos.</span>
    </div>

    <div class="sg-content">
      <SignalGeneratorPanel />
    </div>
  </div>
</template>

<style scoped>
.sg-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: 16px;
  overflow-y: auto;
  padding: 16px;
}

.sg-topbar {
  display: flex;
  flex-direction: column;
  gap: 2px;
  border-bottom: 0.5px solid var(--color-border);
  padding-bottom: 8px;
}

.sg-title {
  font-size: 14px;
  font-weight: 700;
  color: var(--color-text-primary);
}

.sg-subtitle {
  font-size: 11px;
  color: var(--color-text-secondary);
}

.sg-content {
  flex: 1;
}
</style>
