<script setup lang="ts">
import { computed, ref } from 'vue';
import { useAppStore } from '../../stores/useAppStore';
import { useAudioStore } from '../../stores/useAudioStore';
import { useMeasurementSession } from '../../stores/useMeasurementSession';
import { storeToRefs } from 'pinia';
import WorkspacePanel from './WorkspacePanel.vue';
import MagnitudePanel from './panels/MagnitudePanel.vue';
import PhasePanel from './panels/PhasePanel.vue';
import CoherencePanel from './panels/CoherencePanel.vue';
import RTAPanel from './panels/RTAPanel.vue';
import WaveformPanel from './panels/WaveformPanel.vue';
import SignalGeneratorPanel from './panels/SignalGeneratorPanel.vue';
import FilterDesignerPanel from './panels/FilterDesignerPanel.vue';
import IOSetup from './IOSetup.vue';
import { 
  IconPlayerStop, 
  IconUpload, 
  IconFileMusic, 
  IconX, 
  IconActivity,
  IconWaveSine,
  IconFilter
} from '@tabler/icons-vue';

const appStore = useAppStore();
const audioStore = useAudioStore();
const session = useMeasurementSession();

const {
  selectedInputDevice,
  selectedSampleRate,
  selectedBufferSize,
  estimatedLatencyMs,
  levelX_dBFS,
  levelY_dBFS
} = storeToRefs(audioStore);

// --- Dropzones Local State for File Mode ---
const isDragoverX = ref(false);
const isDragoverY = ref(false);
const isLoadingX = ref(false);
const isLoadingY = ref(false);
const errorX = ref<string | null>(null);
const errorY = ref<string | null>(null);
const fileInputX = ref<HTMLInputElement | null>(null);
const fileInputY = ref<HTMLInputElement | null>(null);
const fileSizes = ref<{ x: string | null; y: string | null }>({ x: null, y: null });

const activeToolsTab = ref<'generator' | 'filter'>('generator');

const allPanelsHidden = computed(() => {
  return !appStore.panelVisibility.magnitude &&
         !appStore.panelVisibility.phase &&
         !appStore.panelVisibility.coherence &&
         !appStore.panelVisibility.rta &&
         !appStore.panelVisibility.waveform;
});

const meterWidthX = computed(() => {
  const lvl = levelX_dBFS.value;
  if (lvl === -Infinity || isNaN(lvl)) return 0;
  return Math.max(0, Math.min(100, ((lvl - (-60)) / 60) * 100));
});

const meterWidthY = computed(() => {
  const lvl = levelY_dBFS.value;
  if (lvl === -Infinity || isNaN(lvl)) return 0;
  return Math.max(0, Math.min(100, ((lvl - (-60)) / 60) * 100));
});

function formatDbfs(val: number) {
  if (val === -Infinity || isNaN(val) || val <= -99) return '-inf';
  return val.toFixed(1) + ' dB';
}

function formatBytes(bytes: number, decimals = 1) {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

function formatFs(fs: number) {
  if (fs >= 1000) return (fs / 1000).toFixed(1) + ' kHz';
  return fs + ' Hz';
}

function truncateFilename(name: string, maxLen = 30) {
  if (name.length <= maxLen) return name;
  return name.slice(0, 15) + '...' + name.slice(-10);
}

function triggerFilePicker(slot: 'x' | 'y') {
  if (slot === 'x') {
    fileInputX.value?.click();
  } else {
    fileInputY.value?.click();
  }
}

function onFileSelected(slot: 'x' | 'y', event: Event) {
  const file = (event.target as HTMLInputElement).files?.[0];
  if (file) {
    handleFile(slot, file);
  }
  (event.target as HTMLInputElement).value = '';
}

function onFileDrop(slot: 'x' | 'y', event: DragEvent) {
  const file = event.dataTransfer?.files?.[0];
  if (file) {
    handleFile(slot, file);
  }
}

async function handleFile(slot: 'x' | 'y', file: File) {
  if (slot === 'x') {
    errorX.value = null;
    isLoadingX.value = true;
    fileSizes.value.x = formatBytes(file.size);
  } else {
    errorY.value = null;
    isLoadingY.value = true;
    fileSizes.value.y = formatBytes(file.size);
  }

  try {
    await session.loadSignal(slot, file);
  } catch (e) {
    if (slot === 'x') errorX.value = (e as Error).message;
    else errorY.value = (e as Error).message;
  } finally {
    if (slot === 'x') isLoadingX.value = false;
    else isLoadingY.value = false;
  }
}

function clearSignalSlot(slot: 'x' | 'y') {
  session.clearSignal(slot);
  if (slot === 'x') {
    fileSizes.value.x = null;
    errorX.value = null;
  } else {
    fileSizes.value.y = null;
    errorY.value = null;
  }
}
</script>

<template>
  <div class="workspace-container">
    <!-- MODO: TIEMPO REAL -->
    <template v-if="appStore.appMode === 'realtime'">
      <template v-if="audioStore.streamState !== 'running'">
        <IOSetup />
      </template>

      <template v-else>
        <!-- Dashboard superior en vivo -->
        <div class="stream-dashboard-bar">
          <div class="config-summary">
            <span class="active-dot" :class="{ 'simulating': audioStore.isSimulating }"></span>
            <span class="device-name" :title="audioStore.isSimulating ? 'Modo de simulación de señal de prueba' : selectedInputDevice?.name">
              {{ audioStore.isSimulating ? 'Simulación Activa' : selectedInputDevice?.name }}
            </span>
            <span class="divider">·</span>
            <span class="meta-item">{{ selectedSampleRate / 1000 }} kHz</span>
            <span class="divider">·</span>
            <span class="meta-item">Buf: {{ selectedBufferSize }}</span>
            <span class="divider">·</span>
            <span class="meta-item">{{ estimatedLatencyMs.toFixed(1) }} ms</span>
          </div>

          <div class="meters-container">
            <!-- Canal X (Referencia) -->
            <div class="meter-wrapper">
              <span class="meter-label">Ref X</span>
              <div class="meter-bg">
                <div class="meter-fill fill-x" :style="{ width: meterWidthX + '%' }"></div>
              </div>
              <span class="meter-value" :class="{ 'inf': levelX_dBFS <= -60 }">
                {{ formatDbfs(levelX_dBFS) }}
              </span>
            </div>

            <!-- Canal Y (Medición) -->
            <div class="meter-wrapper">
              <span class="meter-label">Mic Y</span>
              <div class="meter-bg">
                <div class="meter-fill fill-y" :style="{ width: meterWidthY + '%' }"></div>
              </div>
              <span class="meter-value" :class="{ 'inf': levelY_dBFS <= -60 }">
                {{ formatDbfs(levelY_dBFS) }}
              </span>
            </div>
          </div>

          <button @click="audioStore.stopStream" class="btn-stop-stream" title="Detener captura de audio">
            <IconPlayerStop size="14" class="stop-icon" />
            <span>Detener</span>
          </button>
        </div>

        <!-- Contenedor scrollable de paneles (sólo RTA en vivo en modo realtime) -->
        <div class="workspace-panels">
          <WorkspacePanel
            title="Analizador de Espectro en Tiempo Real (RTA)"
            :visible="appStore.panelVisibility.rta"
            @toggle="appStore.togglePanelVisibility('rta')"
          >
            <RTAPanel />
          </WorkspacePanel>

          <div v-if="!appStore.panelVisibility.rta" class="empty-panels-state">
            <div class="empty-text">Activá el panel RTA para ver el resultado</div>
          </div>
        </div>
      </template>
    </template>

    <!-- MODO: CARGA DE ARCHIVOS -->
    <template v-else-if="appStore.appMode === 'file'">
      <!-- Pantalla de carga inicial si no hay señales en memoria -->
      <template v-if="!session.hasSignals">
        <div class="file-setup-container">
          <div class="glass-card file-setup-card">
            <div class="setup-header">
              <div class="logo-badge">
                <IconFileMusic size="24" class="badge-icon" />
              </div>
              <h2 class="title">Análisis de Señales Pregrabadas</h2>
              <p class="subtitle">
                Carga dos archivos de audio (.wav) para calcular y comparar la función de respuesta en frecuencia, fase y coherencia de doble canal.
              </p>
            </div>

            <div class="setup-body">
              <div class="drop-zones-grid">
                <!-- Dropzone X (Referencia) -->
                <div 
                  class="workspace-drop-zone x-channel"
                  :class="{ 'is-dragover': isDragoverX, 'is-loaded': session.x, 'is-loading': isLoadingX }"
                  @dragenter.prevent="isDragoverX = true"
                  @dragleave.prevent="isDragoverX = false"
                  @dragover.prevent
                  @drop.prevent="isDragoverX = false; onFileDrop('x', $event)"
                  @click="triggerFilePicker('x')"
                >
                  <input 
                    type="file" 
                    ref="fileInputX" 
                    style="display: none" 
                    accept=".wav"
                    @change="onFileSelected('x', $event)"
                  />
                  <div v-if="isLoadingX" class="status-inner" @click.stop>
                    <span class="spinner"></span>
                    <span class="loading-text">Cargando archivo X...</span>
                  </div>
                  <div v-else-if="session.x" class="loaded-inner">
                    <div class="channel-badge ref-badge">CANAL X (REFERENCIA)</div>
                    <div class="file-name-main" :title="session.x.filename">
                      {{ truncateFilename(session.x.filename) }}
                    </div>
                    <div class="file-details">
                      <span>Tamaño: {{ fileSizes.x || '—' }}</span>
                      <span>Fs: {{ formatFs(session.x.fs) }}</span>
                      <span>Duración: {{ session.x.duration.toFixed(2) }}s</span>
                    </div>
                    <button class="clear-btn-main" @click.stop="clearSignalSlot('x')">
                      <IconX size="14" />
                      <span>Remover</span>
                    </button>
                  </div>
                  <div v-else class="empty-inner">
                    <div class="upload-icon-wrapper">
                      <IconUpload size="20" />
                    </div>
                    <div class="empty-title">Señal de Referencia (X)</div>
                    <div class="empty-desc">Arrastrá un archivo .wav o hacé click aquí</div>
                    <div v-if="errorX" class="error-inline">{{ errorX }}</div>
                  </div>
                </div>

                <!-- Dropzone Y (Medición) -->
                <div 
                  class="workspace-drop-zone y-channel"
                  :class="{ 'is-dragover': isDragoverY, 'is-loaded': session.y, 'is-loading': isLoadingY }"
                  @dragenter.prevent="isDragoverY = true"
                  @dragleave.prevent="isDragoverY = false"
                  @dragover.prevent
                  @drop.prevent="isDragoverY = false; onFileDrop('y', $event)"
                  @click="triggerFilePicker('y')"
                >
                  <input 
                    type="file" 
                    ref="fileInputY" 
                    style="display: none" 
                    accept=".wav"
                    @change="onFileSelected('y', $event)"
                  />
                  <div v-if="isLoadingY" class="status-inner" @click.stop>
                    <span class="spinner"></span>
                    <span class="loading-text">Cargando archivo Y...</span>
                  </div>
                  <div v-else-if="session.y" class="loaded-inner">
                    <div class="channel-badge meas-badge">CANAL Y (MEDICIÓN)</div>
                    <div class="file-name-main" :title="session.y.filename">
                      {{ truncateFilename(session.y.filename) }}
                    </div>
                    <div class="file-details">
                      <span>Tamaño: {{ fileSizes.y || '—' }}</span>
                      <span>Fs: {{ formatFs(session.y.fs) }}</span>
                      <span>Duración: {{ session.y.duration.toFixed(2) }}s</span>
                    </div>
                    <button class="clear-btn-main" @click.stop="clearSignalSlot('y')">
                      <IconX size="14" />
                      <span>Remover</span>
                    </button>
                  </div>
                  <div v-else class="empty-inner">
                    <div class="upload-icon-wrapper">
                      <IconUpload size="20" />
                    </div>
                    <div class="empty-title">Señal de Medición (Y)</div>
                    <div class="empty-desc">Arrastrá un archivo .wav o hacé click aquí</div>
                    <div v-if="errorY" class="error-inline">{{ errorY }}</div>
                  </div>
                </div>
              </div>

              <!-- Cartel de ayuda e información -->
              <div class="instruction-box">
                <IconActivity size="18" class="instruction-icon" />
                <div class="instruction-content">
                  <span class="instruction-title">¿Cómo funciona el análisis?</span>
                  <p class="instruction-desc">
                    El sistema compara la señal de entrada **X(t)** (Referencia) con la señal de salida **Y(t)** (Medición) obtenida tras pasar por el sistema bajo prueba. A partir de ellas se calcula la función de respuesta en frecuencia **H(ω) = Y(ω) / X(ω)** (magnitud y fase) y la **Coherencia γ²(ω)**. Ambas señales deben poseer la misma frecuencia de muestreo.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- Panel de resultados si ya hay señales -->
      <template v-else>
        <!-- Resumen de Archivos Analizados -->
        <div class="file-summary-bar">
          <div class="file-info-group">
            <span class="bar-title">ARCHIVOS ANALIZADOS:</span>
            <div class="file-badge ref">
              <span class="badge-label">Ref X:</span>
              <span class="badge-name" :title="session.x?.filename">{{ truncateFilename(session.x?.filename ?? '', 20) }}</span>
            </div>
            <span class="badge-arrow">→</span>
            <div class="file-badge meas">
              <span class="badge-label">Mic Y:</span>
              <span class="badge-name" :title="session.y?.filename">{{ truncateFilename(session.y?.filename ?? '', 20) }}</span>
            </div>
            <span class="divider">·</span>
            <span class="meta-item">{{ formatFs(session.x?.fs ?? 44100) }}</span>
            <span class="divider">·</span>
            <div class="bar-controls-group">
              <div class="bar-select-wrapper" title="Tamaño de la FFT para el análisis espectral">
                <span class="select-label">FFT</span>
                <select :value="session.params.windowSize" @change="e => session.updateParams({ windowSize: parseInt((e.target as HTMLSelectElement).value) as 1024 | 2048 | 4096 | 8192 })" class="bar-select">
                  <option :value="1024">1024</option>
                  <option :value="2048">2048</option>
                  <option :value="4096">4096</option>
                  <option :value="8192">8192</option>
                </select>
              </div>
              <div class="bar-select-wrapper" title="Porcentaje de solapamiento entre ventanas de análisis consecutivas">
                <span class="select-label">Solape</span>
                <select :value="session.params.overlap" @change="e => session.updateParams({ overlap: parseFloat((e.target as HTMLSelectElement).value) })" class="bar-select">
                  <option :value="0.0">0%</option>
                  <option :value="0.25">25%</option>
                  <option :value="0.5">50%</option>
                  <option :value="0.75">75%</option>
                  <option :value="0.9">90%</option>
                </select>
              </div>
              <div class="bar-select-wrapper" title="Función de ventana para suavizado de bordes y reducción de fugas espectrales">
                <span class="select-label">Ventana</span>
                <select :value="session.params.windowType" @change="e => session.updateParams({ windowType: (e.target as HTMLSelectElement).value as any })" class="bar-select">
                  <option value="hann">Hann</option>
                  <option value="hamming">Hamming</option>
                  <option value="blackman">Blackman</option>
                  <option value="rectangular">Rectangular</option>
                </select>
              </div>
            </div>
          </div>

          <button @click="session.resetSession()" class="btn-clear-session" title="Limpiar y cargar otros archivos">
            <IconX size="14" />
            <span>Cargar Otros</span>
          </button>
        </div>

        <!-- Contenedor scrollable de paneles -->
        <div class="workspace-panels">
          <WorkspacePanel
            title="Magnitud H(ω)"
            :visible="appStore.panelVisibility.magnitude"
            @toggle="appStore.togglePanelVisibility('magnitude')"
          >
            <MagnitudePanel />
          </WorkspacePanel>

          <WorkspacePanel
            title="Fase"
            :visible="appStore.panelVisibility.phase"
            @toggle="appStore.togglePanelVisibility('phase')"
          >
            <PhasePanel />
          </WorkspacePanel>

          <WorkspacePanel
            title="Coherencia γ²"
            :visible="appStore.panelVisibility.coherence"
            @toggle="appStore.togglePanelVisibility('coherence')"
          >
            <CoherencePanel />
          </WorkspacePanel>

          <WorkspacePanel
            title="Espectro FFT (X e Y superpuestas)"
            :visible="appStore.panelVisibility.rta"
            @toggle="appStore.togglePanelVisibility('rta')"
          >
            <RTAPanel />
          </WorkspacePanel>

          <WorkspacePanel
            title="Forma de onda"
            :visible="appStore.panelVisibility.waveform"
            @toggle="appStore.togglePanelVisibility('waveform')"
          >
            <WaveformPanel />
          </WorkspacePanel>

          <div v-if="allPanelsHidden" class="empty-panels-state">
            <div class="empty-text">Activá al menos un panel</div>
          </div>
        </div>
      </template>
    </template>

    <!-- MODO: GENERADOR Y FILTROS -->
    <template v-else-if="appStore.appMode === 'tools'">
      <div class="tools-workspace">
        <!-- Tab selector superior -->
        <div class="tools-tab-bar">
          <button 
            class="tools-tab-btn" 
            :class="{ active: activeToolsTab === 'generator' }" 
            @click="activeToolsTab = 'generator'"
          >
            <IconWaveSine size="16" />
            <span>Generador de Señales</span>
          </button>
          <button 
            class="tools-tab-btn" 
            :class="{ active: activeToolsTab === 'filter' }" 
            @click="activeToolsTab = 'filter'"
          >
            <IconFilter size="16" />
            <span>Diseñador de Filtros</span>
          </button>
        </div>

        <!-- Tab content container -->
        <div class="tools-tab-content">
          <div class="glass-card tools-card">
            <SignalGeneratorPanel v-if="activeToolsTab === 'generator'" />
            <FilterDesignerPanel v-if="activeToolsTab === 'filter'" />
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.workspace-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 0;
  background-color: var(--color-bg-primary);
}

.stream-dashboard-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 20px;
  background: rgba(24, 28, 36, 0.75);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border-bottom: 1px solid var(--color-border);
  height: 52px;
  flex-shrink: 0;
  gap: 24px;
  z-index: 2;
}

.config-summary {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 11px;
  color: var(--color-text-secondary);
}

.active-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background-color: var(--color-accent);
  box-shadow: 0 0 8px var(--color-accent);
  animation: blink 1.5s infinite alternate;
}

.active-dot.simulating {
  background-color: #818cf8;
  box-shadow: 0 0 8px #818cf8;
}

.device-name {
  font-weight: 500;
  color: var(--color-text-primary);
  max-width: 160px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.divider {
  opacity: 0.3;
}

.meta-item {
  font-family: var(--font-mono);
}

.meters-container {
  display: flex;
  align-items: center;
  gap: 20px;
  flex: 1;
  max-width: 500px;
}

.meter-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.meter-label {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--color-text-secondary);
  width: 32px;
  letter-spacing: 0.5px;
}

.meter-bg {
  height: 8px;
  background: rgba(10, 11, 13, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.02);
  border-radius: 4px;
  flex: 1;
  overflow: hidden;
  position: relative;
}

.meter-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.1s cubic-bezier(0.1, 0.8, 0.3, 1);
}

.fill-x {
  background: linear-gradient(to right, #00d97e 75%, #f59e0b 90%, #ef4444 100%);
}

.fill-y {
  background: linear-gradient(to right, #818cf8 75%, #ec4899 90%, #ef4444 100%);
}

.meter-value {
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--color-text-primary);
  width: 52px;
  text-align: right;
}

.meter-value.inf {
  color: var(--color-text-secondary);
  opacity: 0.5;
}

.btn-stop-stream {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: rgba(239, 68, 68, 0.08);
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: var(--border-radius-md);
  color: #f87171;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-stop-stream:hover {
  background: #ef4444;
  color: #050505;
  border-color: transparent;
  box-shadow: 0 0 10px rgba(239, 68, 68, 0.3);
}

.btn-stop-stream:active {
  transform: scale(0.97);
}

.stop-icon {
  flex-shrink: 0;
}

.workspace-panels {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  min-height: 0;
  padding: 16px;
  gap: 16px;
}

.empty-panels-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  background: var(--color-bg-secondary);
  border-radius: var(--border-radius-lg);
  border: 1px dashed var(--color-border);
}

.empty-text {
  font-size: 13px;
  color: var(--color-text-secondary);
  font-family: var(--font-mono);
  background: var(--color-bg-elevated);
  padding: 8px 16px;
  border-radius: var(--border-radius-md);
  border: 1px solid var(--color-border);
}

@keyframes blink {
  0% { opacity: 0.4; }
  100% { opacity: 1; }
}

/* File Setup Workspace Page */
.file-setup-container {
  display: flex;
  justify-content: center;
  align-items: center;
  flex: 1;
  padding: 40px 20px;
  background-color: var(--color-bg-primary);
  min-height: 0;
  overflow-y: auto;
}

.file-setup-card {
  width: 100%;
  max-width: 720px;
  border-radius: var(--border-radius-lg);
  padding: 32px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
}

.glass-card {
  background: rgba(24, 28, 36, 0.65);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.setup-header {
  text-align: center;
  margin-bottom: 28px;
}

.logo-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 52px;
  height: 52px;
  border-radius: 12px;
  background: var(--color-accent-dim);
  color: var(--color-accent);
  margin-bottom: 16px;
  border: 1px solid rgba(0, 217, 126, 0.2);
  box-shadow: 0 0 15px rgba(0, 217, 126, 0.1);
}

.title {
  font-size: 20px;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: var(--color-text-primary);
  letter-spacing: -0.3px;
}

.subtitle {
  font-size: 13px;
  color: var(--color-text-secondary);
  line-height: 1.5;
  margin: 0;
}

.setup-body {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.drop-zones-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 8px;
}

.workspace-drop-zone {
  border: 1.5px dashed var(--color-border);
  border-radius: var(--border-radius-md);
  padding: 24px 16px;
  cursor: pointer;
  background: rgba(16, 18, 23, 0.4);
  transition: all 0.2s ease;
  position: relative;
  min-height: 180px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  user-select: none;
}

.workspace-drop-zone:hover {
  background: var(--color-bg-elevated);
}

.workspace-drop-zone.x-channel:hover {
  border-color: var(--color-accent);
}

.workspace-drop-zone.y-channel:hover {
  border-color: #818cf8;
}

.workspace-drop-zone.is-dragover {
  border-color: var(--color-accent);
  background: var(--color-accent-dim);
}

.workspace-drop-zone.is-loaded {
  border-style: solid;
  border-color: var(--color-border);
  cursor: default;
  background: rgba(24, 28, 36, 0.6);
}

.upload-icon-wrapper {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-secondary);
  margin-bottom: 12px;
  transition: all 0.2s ease;
}

.workspace-drop-zone:hover .upload-icon-wrapper {
  transform: translateY(-2px);
  color: var(--color-text-primary);
  background: rgba(255, 255, 255, 0.05);
}

.workspace-drop-zone.x-channel:hover .upload-icon-wrapper {
  color: var(--color-accent);
  box-shadow: 0 0 10px rgba(0, 217, 126, 0.1);
}

.workspace-drop-zone.y-channel:hover .upload-icon-wrapper {
  color: #818cf8;
  box-shadow: 0 0 10px rgba(99, 102, 241, 0.1);
}

.empty-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 4px;
}

.empty-desc {
  font-size: 11px;
  color: var(--color-text-secondary);
}

.error-inline {
  font-size: 10px;
  color: #EF4444;
  margin-top: 8px;
}

.channel-badge {
  font-size: 9px;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: 4px;
  letter-spacing: 0.5px;
  margin-bottom: 12px;
}

.ref-badge {
  color: var(--color-accent);
  background: var(--color-accent-dim);
}

.meas-badge {
  color: #818cf8;
  background: rgba(99, 102, 241, 0.12);
}

.file-name-main {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 8px;
  word-break: break-all;
  padding: 0 8px;
}

.file-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 11px;
  color: var(--color-text-secondary);
  margin-bottom: 16px;
}

.clear-btn-main {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 5px 12px;
  background: rgba(239, 68, 68, 0.08);
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: var(--border-radius-md);
  color: #f87171;
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.clear-btn-main:hover {
  background: #ef4444;
  color: #050505;
  border-color: transparent;
}

.spinner {
  width: 24px;
  height: 24px;
  border: 3px solid var(--color-border);
  border-top-color: var(--color-accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  display: inline-block;
  margin-bottom: 12px;
}

.loading-text {
  font-size: 11px;
  color: var(--color-text-secondary);
}

.status-inner {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.loaded-inner {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Instructions Box */
.instruction-box {
  display: flex;
  gap: 16px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-md);
  align-items: flex-start;
  text-align: left;
}

.instruction-icon {
  color: var(--color-accent);
  margin-top: 2px;
  flex-shrink: 0;
}

.instruction-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.instruction-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.instruction-desc {
  font-size: 11px;
  color: var(--color-text-secondary);
  line-height: 1.5;
  margin: 0;
}

/* File Summary Bar */
.file-summary-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 20px;
  background: rgba(24, 28, 36, 0.75);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border-bottom: 1px solid var(--color-border);
  height: 52px;
  flex-shrink: 0;
  gap: 24px;
  z-index: 2;
}

.file-info-group {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 11px;
  color: var(--color-text-secondary);
}

.bar-title {
  font-weight: 700;
  color: var(--color-text-secondary);
  letter-spacing: 0.5px;
}

.file-badge {
  display: flex;
  align-items: center;
  gap: 4px;
  background: var(--color-bg-elevated);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  padding: 2px 6px;
  font-size: 11px;
}

.file-badge.ref .badge-label {
  color: var(--color-accent);
  font-weight: 600;
}

.file-badge.meas .badge-label {
  color: #818cf8;
  font-weight: 600;
}

.file-badge .badge-name {
  color: var(--color-text-primary);
  max-width: 140px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.badge-arrow {
  opacity: 0.5;
}

.btn-clear-session {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: var(--color-bg-elevated);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-md);
  color: var(--color-text-primary);
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-clear-session:hover {
  background: var(--color-border);
  color: #EF4444;
}

.bar-controls-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.bar-select-wrapper {
  display: flex;
  align-items: center;
  gap: 6px;
  background: var(--color-bg-elevated);
  border: 1px solid var(--color-border);
  padding: 2px 6px;
  border-radius: 4px;
}

.select-label {
  font-size: 10px;
  font-weight: 700;
  color: var(--color-text-secondary);
  text-transform: uppercase;
}

.bar-select {
  background: transparent;
  border: none;
  color: var(--color-text-primary);
  font-size: 11px;
  font-family: var(--font-mono);
  outline: none;
  cursor: pointer;
  padding: 0;
}

.bar-select option {
  background-color: var(--surface-3, #1e1e21);
  color: var(--text-white, #ffffff);
}

/* Tools Mode Styles */
.tools-workspace {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 24px;
  gap: 20px;
  background-color: var(--color-bg-primary);
}

.tools-tab-bar {
  display: flex;
  gap: 12px;
  border-bottom: 1px solid var(--color-border);
  padding-bottom: 8px;
}

.tools-tab-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  background: none;
  border: none;
  padding: 8px 16px;
  color: var(--color-text-secondary);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  border-radius: var(--border-radius-md);
  transition: all 0.2s ease;
}

.tools-tab-btn:hover {
  background: rgba(255, 255, 255, 0.03);
  color: var(--color-text-primary);
}

.tools-tab-btn.active {
  background: var(--color-accent-dim);
  color: var(--color-accent);
  box-shadow: 0 2px 8px rgba(0, 217, 126, 0.08);
}

.tools-tab-btn:nth-child(2).active {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
  box-shadow: 0 2px 8px rgba(245, 158, 11, 0.08);
}

.tools-tab-content {
  flex: 1;
  overflow-y: auto;
  min-height: 0;
  display: flex;
}

.tools-card {
  width: 100%;
  border-radius: var(--border-radius-lg);
  padding: 24px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
  min-height: 0;
}
</style>
