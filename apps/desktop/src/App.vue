<script setup lang="ts">
import AppShell from './components/layout/AppShell.vue';
</script>

<template>
  <AppShell />
</template>

<style>
@import './assets/base.css';

/* Global placeholder helpers */
.placeholder {
  text-align: center;
  color: var(--text-silver);
  font-family: var(--font-mono);
  font-size: 13px;
}

.placeholder-sub {
  font-family: var(--font-ui);
  font-size: 13px;
  font-weight: 300;
  color: var(--text-gray);
  margin-top: 8px;
}
</style>
