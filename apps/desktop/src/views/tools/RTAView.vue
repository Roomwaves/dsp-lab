<script setup lang="ts">
import { useAppStore } from '../../stores/app';
import { storeToRefs } from 'pinia';
import { t } from '../../utils/i18n';
import { generateBars } from '../../utils/visualizations';
import { computed } from 'vue';
import { IconPlayerPlay } from '@tabler/icons-vue';

const appStore = useAppStore();
const { language } = storeToRefs(appStore);

const bars = computed(() => generateBars(58));
</script>

<template>
  <div class="tool-wrapper">
    <div class="header">
      <div class="title">{{ t('n-rta', language) }}</div>
      <div class="subtitle">{{ t('frequency', language) }} spectrum · FFT 4096</div>
    </div>
    
    <div class="vis-box">
      <div class="bars-container">
        <div v-for="(height, i) in bars" :key="i" class="bar" :style="{ height: `${height}%` }"></div>
      </div>
      <div class="x-axis">
        <span>20 Hz</span>
        <span>100</span>
        <span>500</span>
        <span>1k</span>
        <span>5k</span>
        <span>20k Hz</span>
      </div>
    </div>
    
    <div class="controls">
      <span class="pill action-btn"><IconPlayerPlay size="12" />{{ t('start', language) }}</span>
      <span class="pill">FFT: 4096</span>
      <span class="pill">44 100 Hz</span>
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
}

.vis-box {
  background: var(--color-background-secondary);
  border: 0.5px solid var(--color-border-tertiary);
  border-radius: var(--border-radius-lg);
  padding: 18px;
}

.bars-container {
  display: flex;
  align-items: flex-end;
  gap: 2px;
  height: 130px;
}

.bar {
  flex: 1;
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

.action-btn {
  cursor: pointer;
}
.action-btn:hover {
  background: var(--color-background-tertiary);
}
</style>
