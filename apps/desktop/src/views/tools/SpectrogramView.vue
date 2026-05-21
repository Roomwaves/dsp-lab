<script setup lang="ts">
const { t } = useI18n();
import { useI18n } from 'vue-i18n';
import { generateSpectrogram } from '../../utils/visualizations';
import { computed } from 'vue';

const cols = 36;
const rows = 7;
const spectrogramData = computed(() => generateSpectrogram(cols, rows));
</script>

<template>
  <div class="tool-wrapper">
    <div class="header">
      <div class="title">{{ t('sidebar.spectrogram') }}</div>
      <div class="subtitle">Time–frequency representation</div>
    </div>
    
    <div class="vis-box">
      <div class="grid-container">
        <div v-for="(col, cIdx) in spectrogramData" :key="cIdx" class="grid-col">
          <div v-for="(val, rIdx) in col" :key="rIdx" class="sbar" :style="{ opacity: val.toFixed(2) }"></div>
        </div>
      </div>
      
      <div class="x-axis">
        <span>0s</span>
        <span>1s</span>
        <span>2s</span>
        <span>3s</span>
        <span>4s</span>
      </div>
    </div>
    
    <div class="controls">
      <span class="pill">FFT: 2048</span>
      <span class="pill">{{ t('controls.window') }}: Hann</span>
      <span class="pill">{{ t('controls.overlap') }}: 75%</span>
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
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-lg);
  padding: 18px;
}

.grid-container {
  display: grid;
  grid-template-columns: repeat(36, 1fr);
  gap: 1px;
  height: 130px;
}

.grid-col {
  display: flex;
  flex-direction: column;
  gap: 1px;
  height: 100%;
}

.sbar {
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
</style>
