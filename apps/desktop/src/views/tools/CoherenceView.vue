<script setup lang="ts">
const { t } = useI18n();
import { useI18n } from 'vue-i18n';

</script>

<template>
  <div class="tool-wrapper">
    <div class="header">
      <div class="title">{{ t('sidebar.coherence') }}</div>
      <div class="subtitle">γ²(ω) = |Gₓᵧ|² / Gₓₓ · Gᵧᵧ</div>
    </div>
    
    <div class="vis-box">
      <div class="chart-container">
        <div class="line top-line"></div>
        <div class="line mid-line"></div>
        <div class="line bot-line"></div>
        <div class="label top-label">1.0</div>
        <div class="label mid-label">0.5</div>
        <div class="label bot-label">0.0</div>
        
        <svg width="100%" height="100%" viewBox="0 0 480 130" preserveAspectRatio="none" aria-hidden="true">
          <polyline points="0,8 60,10 120,14 180,18 240,22 300,50 360,88 420,116 480,120" fill="none" stroke="var(--color-border-success)" stroke-width="1.5"/>
        </svg>
      </div>
      
      <div class="x-axis">
        <span>20 Hz</span>
        <span>1k</span>
        <span>20k Hz</span>
      </div>
    </div>
    
    <div class="controls">
      <span class="pill success-pill">{{ t('controls.high_coh') }}</span>
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
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-lg);
  padding: 18px;
}

.chart-container {
  position: relative;
  height: 130px;
}

.line {
  position: absolute;
  left: 0;
  right: 0;
  height: 1px;
}

.top-line {
  top: 0;
  background: var(--color-border);
}

.mid-line {
  top: 50%;
  background: var(--color-border);
}

.bot-line {
  bottom: 0;
  background: var(--color-border);
}

.label {
  position: absolute;
  right: 6px;
  font-size: 9px;
  font-family: var(--font-mono);
}

.top-label {
  top: 2px;
  color: var(--color-text-success);
}

.mid-label {
  top: 50%;
  color: var(--color-text-tertiary);
}

.bot-label {
  bottom: 2px;
  color: var(--color-text-tertiary);
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
  margin-top: 12px;
  text-align: center;
}

.success-pill {
  color: var(--color-text-success);
  border-color: var(--color-border-success);
}
</style>
