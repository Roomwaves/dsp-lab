<script setup lang="ts">
import { useAppStore } from '../../stores/useAppStore';
const { t } = useI18n();
import { storeToRefs } from 'pinia';
import { useI18n } from 'vue-i18n';
import { IconSettings, IconX, IconChevronRight } from '@tabler/icons-vue';

const appStore = useAppStore();
const { isSettingsOpen, theme, language } = storeToRefs(appStore);

function close() {
  appStore.toggleSettings();
}
</script>

<template>
  <div v-show="isSettingsOpen" class="settings-panel">
    <div class="header">
      <div class="title-container">
        <IconSettings size="16" />
        <span class="title">{{ t('settings.title') }}</span>
      </div>
      <button @click="close" class="close-btn" aria-label="Close settings">
        <IconX size="18" />
      </button>
    </div>
    
    <div class="content">
      <p class="section-label">{{ t('settings.appearance') }}</p>
      
      <div class="s-row">
        <div>
          <div class="row-title">{{ t('settings.theme') }}</div>
          <div class="row-sub">{{ t('settings.theme_sub') }}</div>
        </div>
        <div class="btn-group">
          <button class="opt-btn" :class="{ active: theme === 'light' }" @click="appStore.setTheme('light')">{{ t('settings.theme_light') }}</button>
          <button class="opt-btn" :class="{ active: theme === 'dark' }" @click="appStore.setTheme('dark')">{{ t('settings.theme_dark') }}</button>
        </div>
      </div>
      
      <div class="s-row">
        <div>
          <div class="row-title">{{ t('settings.language') }}</div>
          <div class="row-sub">{{ t('settings.language_sub') }}</div>
        </div>
        <div class="btn-group">
          <button class="opt-btn" :class="{ active: language === 'es' }" @click="appStore.setLanguage('es')">ES</button>
          <button class="opt-btn" :class="{ active: language === 'en' }" @click="appStore.setLanguage('en')">EN</button>
        </div>
      </div>
      
      <div class="divider"></div>
      
      <p class="section-label">{{ t('settings.audio') }}</p>
      
      <div class="s-row">
        <div>
          <div class="row-title">{{ t('settings.input_device') }}</div>
          <div class="row-sub">{{ t('settings.input_device_sub') }}</div>
        </div>
        <IconChevronRight size="15" class="chevron" />
      </div>
      
      <div class="s-row">
        <div>
          <div class="row-title">{{ t('settings.sample_rate') }}</div>
          <div class="row-sub">44 100 Hz</div>
        </div>
        <IconChevronRight size="15" class="chevron" />
      </div>
      
      <div class="s-row">
        <div>
          <div class="row-title">{{ t('settings.buffer_size') }}</div>
          <div class="row-sub">1024 samples</div>
        </div>
        <IconChevronRight size="15" class="chevron" />
      </div>
      
      <div class="divider"></div>
      
      <div class="footer-info">
        dsp-analyzer · v0.1.0-dev · <a href="#" class="link">GitHub</a>
      </div>
    </div>
  </div>
</template>

<style scoped>
.settings-panel {
  position: absolute;
  right: 0;
  top: 0;
  height: 100%;
  width: 272px;
  background: var(--color-background-primary);
  border-left: 0.5px solid var(--color-border-tertiary);
  display: flex;
  flex-direction: column;
  z-index: 10;
}

.header {
  padding: 13px 16px;
  border-bottom: 0.5px solid var(--color-border-tertiary);
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
}

.title-container {
  display: flex;
  align-items: center;
  gap: 8px;
}

.title {
  font-size: 13px;
  font-weight: 500;
}

.close-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  color: var(--color-text-secondary);
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.content {
  padding: 16px;
  flex: 1;
  overflow-y: auto;
}

.section-label {
  font-size: 10px;
  color: var(--color-text-tertiary);
  letter-spacing: 0.07em;
  margin: 0 0 11px;
  font-weight: 500;
  text-transform: uppercase;
}

.s-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 11px 0;
  border-bottom: 0.5px solid var(--color-border-tertiary);
}

.s-row:last-of-type {
  border-bottom: none;
}

.row-title {
  font-size: 13px;
  font-weight: 500;
}

.row-sub {
  font-size: 11px;
  color: var(--color-text-tertiary);
}

.btn-group {
  display: flex;
  gap: 4px;
}

.divider {
  height: 1px;
  background: var(--color-border-tertiary);
  margin: 14px 0;
}

.chevron {
  color: var(--color-text-tertiary);
}

.footer-info {
  font-size: 11px;
  color: var(--color-text-tertiary);
  text-align: center;
}

.link {
  color: var(--color-text-info);
  text-decoration: none;
}
</style>
