<script setup lang="ts">
import AppShell from './components/layout/AppShell.vue';
</script>

<template>
  <AppShell />
</template>

<style>
@import './assets/base.css';

/* Global resets and utilities if any */
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
