<script setup lang="ts">
import FilterDesignerPanel from '../../components/workspace/panels/FilterDesignerPanel.vue';
</script>

<template>
  <div class="fd-view">
    <div class="fd-topbar">
      <span class="fd-title">Diseñador de Filtros</span>
      <span class="fd-subtitle">Análisis de respuesta en frecuencia H(ω) y respuesta al impulso h[n] para Media Móvil, Comb y FIR.</span>
    </div>

    <div class="fd-content">
      <FilterDesignerPanel />
    </div>
  </div>
</template>

<style scoped>
.fd-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: 16px;
  overflow-y: auto;
  padding: 16px;
}

.fd-topbar {
  display: flex;
  flex-direction: column;
  gap: 2px;
  border-bottom: 0.5px solid var(--color-border);
  padding-bottom: 8px;
}

.fd-title {
  font-size: 14px;
  font-weight: 700;
  color: var(--color-text-primary);
}

.fd-subtitle {
  font-size: 11px;
  color: var(--color-text-secondary);
}

.fd-content {
  flex: 1;
}
</style>
