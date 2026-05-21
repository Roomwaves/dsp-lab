<script setup lang="ts">
import { computed } from 'vue';
import { useAppStore } from '../../stores/useAppStore';
import SignalGeneratorPanel from './panels/SignalGeneratorPanel.vue';
import FilterDesignerPanel from './panels/FilterDesignerPanel.vue';

const appStore = useAppStore();

const isOpen = computed(() => appStore.isToolsDrawerOpen);
const activeTab = computed(() => appStore.activeToolsDrawerTab);

const tabs = [
  { id: 'generator' as const, label: 'Generador de Señales' },
  { id: 'filter' as const, label: 'Diseñador de Filtros' },
];

function toggle() {
  appStore.toggleToolsDrawer();
}

function activateTab(tabId: 'generator' | 'filter') {
  if (!appStore.isToolsDrawerOpen) {
    appStore.setToolsDrawerOpen(true);
    appStore.setActiveToolsDrawerTab(tabId);
  } else if (appStore.activeToolsDrawerTab === tabId) {
    appStore.setToolsDrawerOpen(false);
  } else {
    appStore.setActiveToolsDrawerTab(tabId);
  }
}
</script>

<template>
  <div class="tools-drawer" :class="{ 'is-open': isOpen }">
    <!-- Header/Handle — siempre visible, clickeable para abrir/cerrar -->
    <div class="drawer-handle" @click="toggle">
      <div class="drawer-tabs">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          :class="{ 'is-active': activeTab === tab.id }"
          @click.stop="activateTab(tab.id)"
        >
          {{ tab.label }}
        </button>
      </div>
      <span class="drawer-toggle-icon">{{ isOpen ? '▼' : '▲' }}</span>
    </div>
 
    <!-- Contenido — solo visible cuando isOpen -->
    <div v-if="isOpen" class="drawer-content">
      <SignalGeneratorPanel v-if="activeTab === 'generator'" />
      <FilterDesignerPanel v-if="activeTab === 'filter'" />
    </div>
  </div>
</template>

<style scoped>
.tools-drawer {
  background: var(--color-bg-secondary);
  border-top: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  transition: height 0.2s ease;
  height: 36px; /* Collapsed height */
}

.tools-drawer.is-open {
  height: 320px; /* Expanded height */
}

.drawer-handle {
  height: 36px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 16px;
  background: var(--color-bg-elevated);
  cursor: pointer;
  user-select: none;
  border-bottom: 1px solid var(--color-border);
}

.drawer-tabs {
  display: flex;
  gap: 8px;
  height: 100%;
  align-items: center;
}

.drawer-tabs button {
  background: none;
  border: none;
  padding: 6px 12px;
  color: var(--color-text-secondary);
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.15s ease;
}

.drawer-tabs button:hover {
  background: rgba(255, 255, 255, 0.05);
  color: var(--color-text-primary);
}

.drawer-tabs button.is-active {
  background: var(--color-bg-secondary);
  color: var(--color-accent);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.drawer-toggle-icon {
  font-size: 11px;
  color: var(--color-text-secondary);
}

.drawer-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  min-height: 0;
}
</style>
