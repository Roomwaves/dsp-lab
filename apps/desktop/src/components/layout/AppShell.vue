<script setup lang="ts">
import { onMounted } from 'vue';
import { useAudioStore } from '../../stores/useAudioStore';
import AppSidebar from './AppSidebar.vue';
import AppTopBar from './AppTopBar.vue';
import WorkspacePanels from '../workspace/WorkspacePanels.vue';
import ToolsDrawer from '../workspace/ToolsDrawer.vue';

const audioStore = useAudioStore();

onMounted(() => {
  audioStore.loadDevices();
  audioStore.listenToStreamEvents();
});
</script>

<template>
  <div class="app-shell">
    <AppTopBar />

    <div class="app-body">
      <AppSidebar />         <!-- sidebar izquierda: I/O + snapshots (issue #58) -->

      <div class="workspace">
        <WorkspacePanels />  <!-- paneles con toggles (issue #59) -->
        <ToolsDrawer />      <!-- panel inferior colapsable (issue #60) -->
      </div>
    </div>
  </div>
</template>

<style scoped>
.app-shell {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
  background: var(--color-bg-primary);
}

.app-body {
  display: flex;
  flex: 1;
  overflow: hidden;   /* crítico: evita scroll en el shell */
}

.workspace {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 0;       /* fix: flex children pueden colapsar */
}
</style>
