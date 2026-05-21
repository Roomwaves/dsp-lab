<script setup lang="ts">
// Placeholder for Issue #60
</script>

<template>
  <div class="tools-drawer">
    <!-- Panel inferior colapsable -->
  </div>
</template>

<style scoped>
.tools-drawer {
  /* Starts collapsed, height 320px when open */
  height: 0;
  border-top: 1px solid var(--color-border-tertiary);
  background: var(--color-bg-secondary);
  overflow: hidden;
  transition: height 0.3s ease;
}
</style>
