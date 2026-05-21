<script setup lang="ts">
import { useAppStore } from '../../stores/useAppStore';
import { storeToRefs } from 'pinia';
import { t } from '../../utils/i18n';
import { computed } from 'vue';
import { IconActivity, IconChartLine, IconChartHistogram, IconInfinity, IconAdjustmentsHorizontal, IconAntenna } from '@tabler/icons-vue';
// @ts-ignore
import { toolMeta as metaData } from '../../utils/visualizations';

const appStore = useAppStore();
const { activeTool, language } = storeToRefs(appStore);

const title = computed(() => t(metaData[activeTool.value].key, language.value));

const IconComponent = computed(() => {
  switch (activeTool.value) {
    case 'rta': return IconActivity;
    case 'tf': return IconChartLine;
    case 'spec': return IconChartHistogram;
    case 'coh': return IconInfinity;
    case 'flt': return IconAdjustmentsHorizontal;
    case 'gen': return IconAntenna;
    default: return IconActivity;
  }
});

</script>

<template>
  <div class="topbar">
    <component :is="IconComponent" size="17" class="icon" />
    <span class="title">{{ title }}</span>
    
    <div class="status-container">
      <div class="status-dot"></div>
      <span class="status-text">{{ t('ready', language) }}</span>
    </div>
  </div>
</template>

<style scoped>
.topbar {
  height: 45px;
  border-bottom: 0.5px solid var(--color-border-tertiary);
  display: flex;
  align-items: center;
  padding: 0 20px;
  gap: 10px;
  flex-shrink: 0;
}

.icon {
  color: var(--color-text-secondary);
}

.title {
  font-size: 13px;
  font-weight: 500;
}

.status-container {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--color-background-success);
}

.status-text {
  font-size: 12px;
  color: var(--color-text-tertiary);
}
</style>
