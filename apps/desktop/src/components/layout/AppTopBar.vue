<script setup lang="ts">
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRoute } from 'vue-router';
import { IconActivity, IconChartLine, IconChartHistogram, IconInfinity, IconAdjustmentsHorizontal, IconAntenna } from '@tabler/icons-vue';

const { t } = useI18n();
const route = useRoute();

const title = computed(() => {
  const name = route.name as string;
  if (!name) return t('sidebar.rta');
  return t(`sidebar.${name.replace('-', '_')}`);
});

const IconComponent = computed(() => {
  switch (route.name) {
    case 'rta': return IconActivity;
    case 'transfer-function': return IconChartLine;
    case 'spectrogram': return IconChartHistogram;
    case 'coherence': return IconInfinity;
    case 'filter-designer': return IconAdjustmentsHorizontal;
    case 'signal-generator': return IconAntenna;
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
      <span class="status-text">{{ t('status.ready') }}</span>
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
