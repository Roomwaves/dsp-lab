<script setup lang="ts">
import { useAppStore } from '../../stores/useAppStore';
import { useAudioStore } from '../../stores/useAudioStore';
import { storeToRefs } from 'pinia';
import { useI18n } from 'vue-i18n';
import { IconSettings, IconX } from '@tabler/icons-vue';

const { t } = useI18n();
const appStore = useAppStore();
const audioStore = useAudioStore();

const { isSettingsOpen, theme, language } = storeToRefs(appStore);
const { 
  inputDevices, outputDevices, 
  selectedInput, selectedOutput, 
  sampleRate, bufferSize,
  latencyEstimateMs
} = storeToRefs(audioStore);

function close() {
  appStore.toggleSettings();
}
</script>

<template>
  <div class="settings-panel" :class="{ open: isSettingsOpen }">
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
          <button class="opt-btn" :class="{ active: theme === 'system' }" @click="appStore.setTheme('system')">{{ t('settings.theme_system') }}</button>
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
      
      <div class="s-row-col">
        <div>
          <div class="row-title">{{ t('settings.input_device') }}</div>
          <div class="row-sub">{{ t('settings.input_device_sub') }}</div>
        </div>
        <select v-model="selectedInput" class="custom-select mt-1">
          <option v-for="dev in inputDevices" :key="dev.id" :value="dev.id">{{ dev.name }}</option>
        </select>
      </div>

      <div class="s-row-col">
        <div>
          <div class="row-title">{{ t('settings.output_device') }}</div>
          <div class="row-sub">{{ t('settings.output_device_sub') }}</div>
        </div>
        <select v-model="selectedOutput" class="custom-select mt-1">
          <option v-for="dev in outputDevices" :key="dev.id" :value="dev.id">{{ dev.name }}</option>
        </select>
      </div>
      
      <div class="s-row-col">
        <div class="row-title">{{ t('settings.sample_rate') }}</div>
        <select v-model="sampleRate" class="custom-select mt-1">
          <option :value="44100">44100 Hz</option>
          <option :value="48000">48000 Hz</option>
          <option :value="96000">96000 Hz</option>
        </select>
      </div>
      
      <div class="s-row-col">
        <div class="row-title">{{ t('settings.buffer_size') }}</div>
        <select v-model="bufferSize" class="custom-select mt-1">
          <option :value="256">256 samples</option>
          <option :value="512">512 samples</option>
          <option :value="1024">1024 samples</option>
          <option :value="2048">2048 samples</option>
        </select>
        <div class="latency-estimate mt-1">
          {{ t('settings.latency_estimate') }}: {{ latencyEstimateMs.toFixed(1) }} ms
        </div>
      </div>
      
      <div class="divider"></div>
      
      <div class="footer-info">
        dsp-analyzer · v0.1.0-dev · <a href="https://github.com/Roomwaves/dsp-lab" target="_blank" class="link">GitHub</a>
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
  background: var(--color-bg-elevated);
  border-left: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  z-index: 10;
  transform: translateX(100%);
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.settings-panel.open {
  transform: translateX(0);
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
  color: var(--color-text-secondary);
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
  border-bottom: 0.5px solid var(--color-border);
}

.s-row:last-of-type {
  border-bottom: none;
}

.s-row-col {
  display: flex;
  flex-direction: column;
  padding: 11px 0;
  border-bottom: 0.5px solid var(--color-border);
}

.s-row-col:last-of-type {
  border-bottom: none;
}

.row-title {
  font-size: 13px;
  font-weight: 500;
}

.row-sub {
  font-size: 11px;
  color: var(--color-text-secondary);
}

.btn-group {
  display: flex;
  gap: 4px;
}

.opt-btn {
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  color: var(--color-text-secondary);
  border-radius: var(--border-radius-sm);
  padding: 4px 8px;
  font-size: 11px;
  cursor: pointer;
}

.opt-btn.active {
  background: var(--color-accent-dim);
  color: var(--color-accent);
  border-color: transparent;
}

.custom-select {
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  color: var(--color-text-primary);
  border-radius: var(--border-radius-sm);
  padding: 6px;
  font-size: 12px;
  width: 100%;
}

.mt-1 {
  margin-top: 8px;
}

.latency-estimate {
  font-size: 11px;
  color: var(--color-text-secondary);
}

.divider {
  height: 1px;
  background: var(--color-border);
  margin: 14px 0;
}

.chevron {
  color: var(--color-text-secondary);
}

.footer-info {
  font-size: 11px;
  color: var(--color-text-secondary);
  text-align: center;
}

.link {
  color: var(--color-text-info);
  text-decoration: none;
}
</style>
