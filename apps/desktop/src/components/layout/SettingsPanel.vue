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
        DSP-LAB · v0.1.0-dev · <a href="https://github.com/Roomwaves/dsp-lab" target="_blank" class="link">GitHub</a>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* DESIGN_GUIDE §6 — Flat Architectural Glass panel for settings drawer */
.settings-panel {
  position: absolute;
  right: 0;
  top: 0;
  height: 100%;
  width: 272px;
  background: var(--surface-2);
  border-left: 1px solid var(--border-ghost);
  display: flex;
  flex-direction: column;
  z-index: 10;
  transform: translateX(100%);
  /* Direct Ease for drawers (DESIGN_GUIDE §7) */
  transition: transform 0.3s var(--ease-direct);
}

.settings-panel.open {
  transform: translateX(0);
}

.header {
  padding: 13px 16px;
  border-bottom: 1px solid var(--border-ghost);
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
}

.title-container {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-silver);
}

/* Varta 400, min 13px (DESIGN_GUIDE §2) */
.title {
  font-family: var(--font-ui);
  font-size: 13px;
  font-weight: 400;
  color: var(--text-white);
}

.close-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  color: var(--text-gray);
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
  transition: color 0.15s var(--ease-material), background 0.15s var(--ease-material);
}

.close-btn:hover {
  color: var(--text-white);
  background: var(--surface-3);
}

.content {
  padding: 16px;
  flex: 1;
  overflow-y: auto;
}

/* Section label — Varta 300, small caps */
.section-label {
  font-family: var(--font-ui);
  font-size: 10px;
  font-weight: 300;
  color: var(--text-gray);
  letter-spacing: 0.09em;
  margin: 0 0 11px;
  text-transform: uppercase;
}

.s-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 11px 0;
  border-bottom: 1px solid var(--border-ghost);
}

.s-row:last-of-type {
  border-bottom: none;
}

.s-row-col {
  display: flex;
  flex-direction: column;
  padding: 11px 0;
  border-bottom: 1px solid var(--border-ghost);
}

.s-row-col:last-of-type {
  border-bottom: none;
}

/* min 13px per DESIGN_GUIDE §2-B */
.row-title {
  font-family: var(--font-ui);
  font-size: 13px;
  font-weight: 400;
  color: var(--text-white);
}

.row-sub {
  font-family: var(--font-ui);
  font-size: 13px;
  font-weight: 300;
  color: var(--text-gray);
  margin-top: 2px;
}

.btn-group {
  display: flex;
  gap: 4px;
}

/* Utility Tonal Button (DESIGN_GUIDE §5) */
.opt-btn {
  background: var(--surface-3);
  border: 1px solid var(--border-default);
  color: var(--text-silver);
  border-radius: var(--radius-sm);
  padding: 5px 10px;
  font-family: var(--font-ui);
  font-size: 13px;
  font-weight: 300;
  cursor: pointer;
  transition: all 0.15s var(--ease-material);
}

.opt-btn:hover:not(.active) {
  background: var(--surface-4);
  border-color: var(--border-bold);
  color: var(--text-white);
}

.opt-btn.active {
  background: var(--accent-lime-10);
  color: var(--accent-lime);
  border-color: var(--border-bold);
}

/* Utility control: select */
.custom-select {
  background: var(--surface-3);
  border: 1px solid var(--border-default);
  color: var(--text-white);
  border-radius: var(--radius-sm);
  padding: 7px 8px;
  font-family: var(--font-ui);
  font-size: 13px;
  font-weight: 300;
  width: 100%;
  cursor: pointer;
  outline: none;
  transition: border-color 0.15s var(--ease-material);
}

.custom-select:focus {
  border-color: var(--border-bold);
}

.mt-1 {
  margin-top: 8px;
}

/* JetBrains Mono for metric values (DESIGN_GUIDE §2-A) */
.latency-estimate {
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 400;
  color: var(--text-gray);
}

.divider {
  height: 1px;
  background: var(--border-ghost);
  margin: 14px 0;
}

.chevron {
  color: var(--text-gray);
}

.footer-info {
  font-family: var(--font-ui);
  font-size: 13px;
  font-weight: 300;
  color: var(--text-gray);
  text-align: center;
}

.link {
  color: var(--accent-lime);
  text-decoration: none;
  transition: color 0.15s var(--ease-material);
}

.link:hover {
  color: var(--accent-lime-pressed);
}
</style>
