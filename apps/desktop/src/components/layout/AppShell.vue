<script setup lang="ts">
import AppSidebar from './AppSidebar.vue';
import AppTopBar from './AppTopBar.vue';
import SettingsPanel from './SettingsPanel.vue';
import { RouterView } from 'vue-router';
</script>

<template>
  <div class="app-layout">
    <AppSidebar />

    <div class="main-content">
      <AppTopBar />
      
      <div class="tool-container">
        <RouterView />
      </div>
    </div>

    <SettingsPanel />
  </div>
</template>

<style scoped>
.app-layout {
  display: flex;
  height: 100vh;
  width: 100vw;
  background-color: var(--color-bg-primary);
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
</style>
