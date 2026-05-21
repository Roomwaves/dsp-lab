<script setup lang="ts">
import { useAppStore, type ToolId } from '../../stores/useAppStore';
const { t } = useI18n();
import { storeToRefs } from 'pinia';
import { useI18n } from 'vue-i18n';
import { IconWaveSine, IconActivity, IconChartLine, IconChartHistogram, IconInfinity, IconAdjustmentsHorizontal, IconAntenna, IconBuilding, IconClock, IconSettings, IconChevronRight } from '@tabler/icons-vue';

const appStore = useAppStore();
const { activeTool } = storeToRefs(appStore);

function pick(id: ToolId) {
  appStore.setActiveTool(id);
}
</script>

<template>
  <div class="sidebar">
    <div class="header">
      <div class="logo">
        <IconWaveSine size="14" class="logo-icon" />
      </div>
      <div>
        <div class="title">dsp-analyzer</div>
        <div class="version">v0.1.0-dev</div>
      </div>
    </div>

    <nav class="nav">
      <p class="sec-label">{{ t('sidebar.analysis') }}</p>
      
      <div class="nav-item" :class="{ active: activeTool === 'rta' }" @click="pick('rta')">
        <IconActivity size="17" /><span>{{ t('sidebar.rta') }}</span>
      </div>
      <div class="nav-item" :class="{ active: activeTool === 'tf' }" @click="pick('tf')">
        <IconChartLine size="17" /><span>{{ t('sidebar.transfer_function') }}</span>
      </div>
      <div class="nav-item" :class="{ active: activeTool === 'spec' }" @click="pick('spec')">
        <IconChartHistogram size="17" /><span>{{ t('sidebar.spectrogram') }}</span>
      </div>
      <div class="nav-item" :class="{ active: activeTool === 'coh' }" @click="pick('coh')">
        <IconInfinity size="17" /><span>{{ t('sidebar.coherence') }}</span>
      </div>

      <div class="divider"></div>
      
      <p class="sec-label">{{ t('sidebar.tools') }}</p>
      <div class="nav-item" :class="{ active: activeTool === 'flt' }" @click="pick('flt')">
        <IconAdjustmentsHorizontal size="17" /><span>{{ t('sidebar.filter_designer') }}</span>
      </div>
      <div class="nav-item" :class="{ active: activeTool === 'gen' }" @click="pick('gen')">
        <IconAntenna size="17" /><span>{{ t('sidebar.signal_generator') }}</span>
      </div>

      <div class="divider"></div>
      
      <p class="sec-label">{{ t('sidebar.soon') }}</p>
      <div class="nav-item disabled">
        <IconBuilding size="17" /><span>{{ t('sidebar.room') }}</span>
        <span class="badge">soon</span>
      </div>
      <div class="nav-item disabled">
        <IconClock size="17" /><span>{{ t('sidebar.delay') }}</span>
        <span class="badge">soon</span>
      </div>
    </nav>

    <div class="footer">
      <div class="nav-item settings-btn" @click="appStore.toggleSettings()">
        <div class="settings-content">
          <IconSettings size="17" />
          <span>{{ t('sidebar.settings') }}</span>
        </div>
        <IconChevronRight size="13" class="chevron" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.sidebar {
  width: 206px;
  min-width: 206px;
  background: var(--color-background-secondary);
  border-right: 0.5px solid var(--color-border-tertiary);
  display: flex;
  flex-direction: column;
}

.header {
  padding: 13px 15px;
  border-bottom: 0.5px solid var(--color-border-tertiary);
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo {
  width: 26px;
  height: 26px;
  border-radius: 7px;
  background: var(--color-background-info);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.logo-icon {
  color: var(--color-text-info);
}

.title {
  font-size: 13px;
  font-weight: 500;
  font-family: var(--font-mono);
  line-height: 1.2;
}

.version {
  font-size: 10px;
  color: var(--color-text-tertiary);
}

.nav {
  flex: 1;
  padding: 10px 8px;
  overflow-y: auto;
}

.sec-label {
  font-size: 10px;
  color: var(--color-text-tertiary);
  letter-spacing: 0.07em;
  padding: 0 12px;
  margin: 0 0 5px;
  font-weight: 500;
  text-transform: uppercase;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 7px 12px;
  border-radius: var(--border-radius-md);
  cursor: pointer;
  font-size: 13px;
  color: var(--color-text-secondary);
  transition: background 0.12s, color 0.12s;
  user-select: none;
}

.nav-item:hover {
  background: var(--color-background-tertiary);
  color: var(--color-text-primary);
}

.nav-item.active {
  background: var(--color-background-info);
  color: var(--color-text-info);
}

.nav-item.disabled {
  opacity: 0.38;
  cursor: not-allowed;
  pointer-events: none;
}

.divider {
  height: 1px;
  background: var(--color-border-tertiary);
  margin: 9px 4px;
}

.badge {
  margin-left: auto;
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 10px;
  background: var(--color-background-tertiary);
  color: var(--color-text-tertiary);
}

.footer {
  padding: 8px;
  border-top: 0.5px solid var(--color-border-tertiary);
}

.settings-btn {
  justify-content: space-between;
}

.settings-content {
  display: flex;
  align-items: center;
  gap: 10px;
}

.chevron {
  color: var(--color-text-tertiary);
}
</style>
