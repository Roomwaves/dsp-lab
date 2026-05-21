<script setup lang="ts">
import { useAppStore } from '../../stores/useAppStore';
import { storeToRefs } from 'pinia';
import { t } from '../../utils/i18n';
import { generateBars } from '../../utils/visualizations';
import { computed, ref } from 'vue';

const appStore = useAppStore();
const { language } = storeToRefs(appStore);

const activeFilter = ref(0);
const filters = ['Moving Average', 'Comb Filter', 'FIR'];

const bars = computed(() => generateBars(28, true));
</script>

<template>
  <div class="tool-wrapper">
    <div class="header">
      <div class="title">{{ t('n-flt', language) }}</div>
      <div class="subtitle">Moving average · Comb · FIR</div>
    </div>
    
    <div class="filter-grid">
      <div 
        v-for="(f, i) in filters" 
        :key="i" 
        class="filter-card"
        :class="{ active: activeFilter === i }"
        @click="activeFilter = i"
      >
        <div class="filter-title">{{ f }}</div>
        <div class="filter-subtitle">h[n]</div>
      </div>
    </div>
    
    <div class="vis-box">
      <div class="equation">h[n] = 1/M &nbsp;&nbsp; M = 8</div>
      <div class="bars-container">
        <div v-for="(height, i) in bars" :key="i" class="bar" :style="{ height: `${height}%` }"></div>
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

.filter-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 8px;
  margin-bottom: 12px;
}

.filter-card {
  background: var(--color-background-secondary);
  border: 0.5px solid var(--color-border-tertiary);
  border-radius: var(--border-radius-md);
  padding: 12px;
  cursor: pointer;
  text-align: center;
}

.filter-card.active {
  border-color: var(--color-border-info);
}

.filter-title {
  font-size: 12px;
  font-weight: 500;
  color: var(--color-text-secondary);
}

.filter-card.active .filter-title {
  color: var(--color-text-info);
}

.filter-subtitle {
  font-size: 10px;
  color: var(--color-text-tertiary);
  margin-top: 3px;
}

.vis-box {
  background: var(--color-background-secondary);
  border: 0.5px solid var(--color-border-tertiary);
  border-radius: var(--border-radius-lg);
  padding: 16px;
}

.equation {
  font-size: 10px;
  color: var(--color-text-tertiary);
  margin-bottom: 8px;
  font-family: var(--font-mono);
}

.bars-container {
  display: flex;
  align-items: flex-end;
  gap: 2px;
  height: 72px;
}

.bar {
  flex: 1;
}
</style>
