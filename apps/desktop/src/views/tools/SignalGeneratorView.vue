<script setup lang="ts">
import { useAppStore } from '../../stores/app';
import { storeToRefs } from 'pinia';
import { t } from '../../utils/i18n';
import { generateSinePoints } from '../../utils/visualizations';
import { computed } from 'vue';

const appStore = useAppStore();
const { language } = storeToRefs(appStore);

const sinePoints = computed(() => generateSinePoints());
</script>

<template>
  <div class="tool-wrapper">
    <div class="header">
      <div class="title">{{ t('n-gen', language) }}</div>
      <div class="subtitle">Pure tones + white noise</div>
    </div>
    
    <div class="vis-box">
      <svg width="100%" height="100" viewBox="0 480 100" preserveAspectRatio="none" style="display:block;" aria-hidden="true">
        <polyline :points="sinePoints" fill="none" stroke="var(--color-border-info)" stroke-width="1.5"/>
      </svg>
      
      <div class="stats-grid">
        <div class="stat-box text-left">
          <div class="stat-label">{{ t('frequency', language) }}</div>
          <div class="stat-value">440 Hz</div>
        </div>
        <div class="stat-box text-center">
          <div class="stat-label">{{ t('amplitude', language) }}</div>
          <div class="stat-value">1.00</div>
        </div>
        <div class="stat-box text-right">
          <div class="stat-label">SNR</div>
          <div class="stat-value">20 dB</div>
        </div>
      </div>
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

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 0;
  margin-top: 14px;
}

.stat-box {
  padding: 0 8px;
}

.text-left {
  text-align: left;
}

.text-center {
  text-align: center;
}

.text-right {
  text-align: right;
}

.stat-label {
  font-size: 10px;
  color: var(--color-text-tertiary);
  margin-bottom: 3px;
}

.stat-value {
  font-size: 14px;
  font-weight: 500;
  font-family: var(--font-mono);
}
</style>
