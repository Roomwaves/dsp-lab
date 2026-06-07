<script setup lang="ts">
import { onMounted } from 'vue';
import { useAudioStore } from '../../stores/useAudioStore';
import { useAppStore } from '../../stores/useAppStore';
import { 
  IconActivity, 
  IconFileMusic, 
  IconChevronRight,
  IconWaveSine
} from '@tabler/icons-vue';
import AppSidebar from './AppSidebar.vue';
import AppTopBar from './AppTopBar.vue';
import WorkspacePanels from '../workspace/WorkspacePanels.vue';

const audioStore = useAudioStore();
const appStore = useAppStore();

function selectMode(mode: 'realtime' | 'file' | 'tools') {
  appStore.setAppMode(mode);
}

onMounted(() => {
  audioStore.loadDevices();
  audioStore.listenToStreamEvents();
});
</script>

<template>
  <!-- Welcome Screen (Mode Selection) -->
  <div v-if="appStore.appMode === null" class="welcome-screen">
    <div class="welcome-content">
      <div class="welcome-header">
        <div class="welcome-logo-container">
          <img src="/logo-test3.svg" alt="RoomWaves Logo" class="welcome-logo-img" />
        </div>
        <h1 class="welcome-title">DSP-LAB</h1>
        <p class="welcome-subtitle">
          Herramienta interactiva para análisis espectral, acústico y funciones de transferencia de doble canal.
        </p>
      </div>

      <div class="mode-cards">
        <!-- Tarjeta 1: Tiempo Real -->
        <div class="mode-card realtime" @click="selectMode('realtime')">
          <div class="card-icon-wrapper">
            <IconActivity size="32" class="card-icon" />
          </div>
          <h2 class="card-title">Analizador en Tiempo Real</h2>
          <p class="card-description">
            Mide y visualiza el espectro RTA, fase y magnitud en vivo utilizando tu hardware de audio o nuestro simulador integrado.
          </p>
          <div class="card-action-btn">
            <span>Comenzar</span>
            <IconChevronRight size="16" />
          </div>
        </div>

        <!-- Tarjeta 2: Carga de Archivos -->
        <div class="mode-card file" @click="selectMode('file')">
          <div class="card-icon-wrapper">
            <IconFileMusic size="32" class="card-icon" />
          </div>
          <h2 class="card-title">Analizador de Archivos</h2>
          <p class="card-description">
            Carga y compara archivos de audio pregrabados (.wav) de la cátedra para analizar funciones de transferencia estáticas y coherencia.
          </p>
          <div class="card-action-btn">
            <span>Comenzar</span>
            <IconChevronRight size="16" />
          </div>
        </div>

        <!-- Tarjeta 3: Generador y Filtros -->
        <div class="mode-card tools" @click="selectMode('tools')">
          <div class="card-icon-wrapper">
            <IconWaveSine size="32" class="card-icon" />
          </div>
          <h2 class="card-title">Generador y Filtros</h2>
          <p class="card-description">
            Genera señales de prueba puras o con ruido, y analiza la respuesta en frecuencia de filtros diseñados (Moving Average, Comb, FIR).
          </p>
          <div class="card-action-btn">
            <span>Comenzar</span>
            <IconChevronRight size="16" />
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Main App Shell -->
  <div v-else class="app-shell">
    <AppTopBar />

    <div class="app-body">
      <AppSidebar />

      <div class="workspace">
        <WorkspacePanels />
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ── Shell layout ───────────────────────────────────────────── */
.app-shell {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
  background: var(--surface-0);
}

.app-body {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.workspace {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 0;
}

/* ══════════════════════════════════════════════════════════════
   WELCOME SCREEN
   Pure black base, Flat Architectural Glass cards
   DESIGN_GUIDE §6 + §1
   ══════════════════════════════════════════════════════════════ */
.welcome-screen {
  position: absolute;
  inset: 0;
  background: var(--surface-0);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 999;
  padding: 24px;
  /* Subtle radial sage breath on background */
  background-image:
    radial-gradient(ellipse 60% 40% at 50% 0%, rgba(131, 188, 169, 0.06) 0%, transparent 70%);
}

.welcome-content {
  max-width: 1000px;
  width: 100%;
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 52px;
}

/* ── Header block ──────────────────────────────────────────── */
.welcome-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 18px;
}

.welcome-logo-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 10px 20px;
  border-radius: var(--radius-lg);
  background: var(--accent-lime-05);
  border: 1px solid var(--border-default);
  box-shadow: 4px 4px 0px 0px var(--surface-0);
  margin-bottom: 4px;
}

.welcome-logo-img {
  height: 36px;
  width: auto;
}

/* Varta — weight 300, wide-spaced minimal (DESIGN_GUIDE §2-A) */
.welcome-title {
  font-family: var(--font-ui);
  font-size: 22px;
  font-weight: 300;
  line-height: 1.1;
  margin: 0;
  color: var(--text-silver);
  letter-spacing: 0.35em;
  text-transform: uppercase;
}

.welcome-title .accent {
  color: var(--accent-lime);
}

/* Varta 300 subtitle, min 13px */
.welcome-subtitle {
  font-family: var(--font-ui);
  font-size: 15px;
  font-weight: 300;
  color: var(--text-silver);
  max-width: 520px;
  line-height: 1.65;
  margin: 0;
}

/* ── Mode cards grid ───────────────────────────────────────── */
.mode-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

/* Flat Architectural Glass Card (DESIGN_GUIDE §6) */
.mode-card {
  background: rgba(0, 26, 35, 0.65);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.20);
  border-radius: var(--radius-md);
  padding: 32px 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  cursor: pointer;
  /* Neo-Brutalist offset shadow */
  box-shadow: 4px 4px 0px 0px var(--surface-0);
  transition: all 0.15s var(--ease-material);
  position: relative;
  overflow: hidden;
}

/* 3D Lift Animation on hover (DESIGN_GUIDE §6) */
.mode-card:hover {
  transform: translate(-3px, -3px);
}

/* Sage accent card (Realtime) — active shadow uses accent-lime */
.mode-card.realtime:hover {
  box-shadow: 4px 4px 0px 0px var(--accent-lime);
  border-color: rgba(131, 188, 169, 0.5);
}

/* Peach accent card (Files) — DESIGN_GUIDE §1 secondary accent */
.mode-card.file:hover {
  box-shadow: 4px 4px 0px 0px var(--accent-peach);
  border-color: rgba(224, 159, 103, 0.5);
}

/* Tools card — sage default */
.mode-card.tools:hover {
  box-shadow: 4px 4px 0px 0px var(--accent-lime);
  border-color: rgba(131, 188, 169, 0.4);
}

/* ── Card icon tile (Elevated Tonal, DESIGN_GUIDE §6) ──────── */
.card-icon-wrapper {
  width: 60px;
  height: 60px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 22px;
  background: var(--surface-2);
  border: 1px solid var(--border-ghost);
  transition: all 0.15s var(--ease-material);
}

.realtime .card-icon-wrapper { color: var(--accent-lime); }
.file .card-icon-wrapper      { color: var(--accent-peach); }
.tools .card-icon-wrapper     { color: var(--accent-lime); }

.realtime:hover .card-icon-wrapper {
  background: var(--accent-lime-10);
  border-color: var(--border-bold);
  box-shadow: 0 0 16px rgba(131, 188, 169, 0.2);
}

.file:hover .card-icon-wrapper {
  background: rgba(224, 159, 103, 0.10);
  border-color: rgba(224, 159, 103, 0.4);
  box-shadow: 0 0 16px rgba(224, 159, 103, 0.2);
}

.tools:hover .card-icon-wrapper {
  background: var(--accent-lime-10);
  border-color: var(--border-bold);
  box-shadow: 0 0 16px rgba(131, 188, 169, 0.2);
}

/* ── Card typography (Varta, min 13px, DESIGN_GUIDE §2) ────── */
.card-title {
  font-family: var(--font-ui);
  font-size: 18px;
  font-weight: 400;
  margin: 0 0 12px 0;
  color: var(--text-white);
  line-height: 1.2;
}

.card-description {
  font-family: var(--font-ui);
  font-size: 13px;
  font-weight: 300;
  color: var(--text-silver);
  line-height: 1.65;
  margin: 0 0 24px 0;
  flex: 1;
}

/* Utility Tonal Button style for card CTA (DESIGN_GUIDE §5) */
.card-action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  font-family: var(--font-ui);
  font-size: 13px;
  font-weight: 400;
  letter-spacing: 0.03em;
  padding: 7px 16px;
  border-radius: var(--radius-sm);
  background: var(--surface-2);
  border: 1px solid var(--border-default);
  transition: all 0.15s var(--ease-material);
}

.realtime .card-action-btn { color: var(--accent-lime); }
.file .card-action-btn      { color: var(--accent-peach); }
.tools .card-action-btn     { color: var(--accent-lime); }

.realtime:hover .card-action-btn {
  background: var(--accent-lime-20);
  border-color: var(--border-bold);
  color: var(--text-white);
}

.file:hover .card-action-btn {
  background: rgba(224, 159, 103, 0.15);
  border-color: rgba(224, 159, 103, 0.5);
  color: var(--text-white);
}

.tools:hover .card-action-btn {
  background: var(--accent-lime-20);
  border-color: var(--border-bold);
  color: var(--text-white);
}
</style>
