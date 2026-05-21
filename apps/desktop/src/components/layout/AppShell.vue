<script setup lang="ts">
import AppSidebar from './AppSidebar.vue';
import AppTopBar from './AppTopBar.vue';
import WorkspacePanels from './WorkspacePanels.vue';
import ToolsDrawer from './ToolsDrawer.vue';
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
