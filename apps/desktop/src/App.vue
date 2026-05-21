<script setup lang="ts">
import { useAppStore } from './stores/useAppStore';
import { storeToRefs } from 'pinia';
import { computed } from 'vue';
import Sidebar from './components/layout/Sidebar.vue';
import TopBar from './components/layout/TopBar.vue';
import SettingsPanel from './components/layout/SettingsPanel.vue';

import RealTimeAnalyzer from './views/tools/RealTimeAnalyzer.vue';
import TransferFunction from './views/tools/TransferFunction.vue';
import Spectrogram from './views/tools/Spectrogram.vue';
import Coherence from './views/tools/Coherence.vue';
import FilterDesigner from './views/tools/FilterDesigner.vue';
import SignalGenerator from './views/tools/SignalGenerator.vue';

const appStore = useAppStore();
const { activeTool } = storeToRefs(appStore);

const currentToolComponent = computed(() => {
  switch (activeTool.value) {
    case 'rta': return RealTimeAnalyzer;
    case 'tf': return TransferFunction;
    case 'spec': return Spectrogram;
    case 'coh': return Coherence;
    case 'flt': return FilterDesigner;
    case 'gen': return SignalGenerator;
    default: return RealTimeAnalyzer;
  }
});
</script>

<template>
  <div class="app-layout">
    <Sidebar />

    <div class="main-content">
      <TopBar />
      
      <div class="tool-container">
        <component :is="currentToolComponent" />
      </div>
    </div>

    <SettingsPanel />
  </div>
</template>

<style>
@import './assets/base.css';

.app-layout {
  display: flex;
  height: 100vh;
  width: 100vw;
  background-color: var(--color-background-primary);
  overflow: hidden;
  position: relative;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.tool-container {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 28px;
  overflow: auto;
}

.placeholder {
  text-align: center;
  color: var(--color-text-secondary);
  font-family: var(--font-mono);
}

.placeholder-sub {
  font-size: 12px;
  color: var(--color-text-tertiary);
  margin-top: 8px;
}
</style>
