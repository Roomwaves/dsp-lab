<script setup lang="ts">
const { t } = useI18n();
import { useI18n } from 'vue-i18n';

</script>

<template>
  <div class="tool-wrapper">
    <div class="header">
      <div class="title">{{ t('sidebar.transfer_function') }}</div>
      <div class="subtitle">H(ω) = Y(ω) / X(ω)</div>
    </div>
    
    <div class="vis-box">
      <svg width="100%" height="130" viewBox="0 0 480 130" preserveAspectRatio="none" aria-hidden="true">
        <polyline points="0,100 50,88 100,68 150,46 200,42 240,44 280,50 330,68 380,95 430,108 480,105" fill="none" stroke="var(--color-border-info)" stroke-width="1.5"/>
        <polyline points="0,72 50,64 100,54 150,36 200,34 240,40 280,48 330,62 380,84 430,96 480,94" fill="none" stroke="var(--color-border-secondary)" stroke-width="1" stroke-dasharray="5,4"/>
      </svg>
      
      <div class="x-axis">
        <span>20 Hz</span>
        <span>100</span>
        <span>1k</span>
        <span>10k</span>
        <span>20k Hz</span>
      </div>
    </div>
    
    <div class="controls">
      <span class="pill">Ch1 {{ t('controls.input') }}</span>
      <span class="pill">Ch2 {{ t('controls.output') }}</span>
      <span class="pill">Avg: 8</span>
    </div>
  </div>
</template>

<style scoped>
.tool-wrapper {
  width: 100%;
  max-width: 500px;
}

.header {
  text-align: center;
  margin-bottom: 20px;
}

.title {
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 3px;
}

.subtitle {
  font-size: 11px;
  color: var(--color-text-tertiary);
  font-family: var(--font-mono);
}

.vis-box {
  background: var(--color-background-secondary);
  border: 0.5px solid var(--color-border-tertiary);
  border-radius: var(--border-radius-lg);
  padding: 18px;
}

.x-axis {
  display: flex;
  justify-content: space-between;
  font-size: 10px;
  color: var(--color-text-tertiary);
  font-family: var(--font-mono);
  margin-top: 6px;
}

.controls {
  display: flex;
  gap: 8px;
  margin-top: 12px;
  justify-content: center;
  flex-wrap: wrap;
}
</style>
