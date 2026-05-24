<script setup lang="ts">
defineProps<{ title: string; visible: boolean }>()
defineEmits<{ toggle: [] }>()
</script>

<template>
  <div class="workspace-panel" :class="{ 'is-hidden': !visible }">
    <div class="panel-header" @click="$emit('toggle')">
      <span class="panel-title">{{ title }}</span>
      <button class="panel-toggle" :aria-label="visible ? 'Ocultar panel' : 'Mostrar panel'">
        {{ visible ? '▼' : '▶' }}
      </button>
    </div>
    <div v-if="visible" class="panel-content">
      <slot />
    </div>
  </div>
</template>

<style scoped>
/* cuando está oculto, no ocupa espacio */
.workspace-panel.is-hidden .panel-content { display: none; }
.workspace-panel { border-bottom: 1px solid var(--color-border); }
.panel-header { 
  display: flex; justify-content: space-between; align-items: center;
  padding: 8px 16px; cursor: pointer; user-select: none;
  background: var(--color-bg-secondary);
}
.panel-header:hover { background: var(--color-bg-elevated); }
.panel-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.panel-toggle {
  background: none;
  border: none;
  color: var(--color-text-secondary);
  cursor: pointer;
  font-size: 11px;
}
.panel-content { padding: 16px; }
</style>
