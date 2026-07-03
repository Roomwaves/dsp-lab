<script setup lang="ts">
import { ref, watch } from 'vue';
import { useAppStore } from '../../stores/useAppStore';
import { useMeasurementSession } from '../../stores/useMeasurementSession';
import { useAudioStore } from '../../stores/useAudioStore';
import { useI18n } from 'vue-i18n';
import { 
  IconSettings, 
  IconChevronRight, 
  IconArrowLeft 
} from '@tabler/icons-vue';

const { t } = useI18n();
const appStore = useAppStore();
const audioStore = useAudioStore();
const session = useMeasurementSession();

// Inline edit state for snapshot labels
const editingId = ref<string | null>(null);
const editingLabel = ref('');

// Parameter selections
const fftSize = ref(session.params.windowSize);
const overlap = ref(session.params.overlap);
const windowType = ref(session.params.windowType);

let debounceTimer: ReturnType<typeof setTimeout> | null = null;

function updateParamsDebounced() {
  if (debounceTimer) clearTimeout(debounceTimer);
  debounceTimer = setTimeout(async () => {
    await session.updateParams({
      windowSize: fftSize.value,
      overlap: overlap.value,
      windowType: windowType.value
    });
  }, 300);
}

watch([fftSize, overlap, windowType], () => {
  updateParamsDebounced();
});

watch(() => session.params, (newParams) => {
  if (newParams) {
    fftSize.value = newParams.windowSize;
    overlap.value = newParams.overlap;
    windowType.value = newParams.windowType;
  }
}, { deep: true });

function startEdit(s: any) {
  editingId.value = s.id;
  editingLabel.value = s.label;
}

function saveEdit(id: string) {
  if (editingId.value === id) {
    const val = editingLabel.value.trim();
    if (val) {
      session.renameSnapshot(id, val);
    }
    editingId.value = null;
  }
}

function cancelEdit() {
  editingId.value = null;
}

function deleteSnapshot(id: string) {
  if (session.snapshots.length === 1) {
    if (!confirm('¿Estás seguro de que deseas eliminar la última captura?')) {
      return;
    }
  }
  session.removeSnapshot(id);
}
</script>

<template>
  <div class="sidebar">
    <!-- Header -->
    <div class="header">
      <div class="logo">
        <img src="/path190.svg" alt="RoomWaves Icon" class="logo-img" />
      </div>
      <div>
        <div class="title">DSP-LAB</div>
        <div class="version">v0.1.0</div>
      </div>
    </div>

    <!-- Sidebar content -->
    <div class="sidebar-content">
      <!-- Back to selection screen button -->
      <button class="back-home-btn" @click="appStore.setAppMode(null)">
        <IconArrowLeft size="14" />
        <span>Cambiar de Modo</span>
      </button>

      <!-- Mode indicator -->
      <div class="mode-indicator">
        <span class="mode-badge" :class="appStore.appMode">
          {{ appStore.appMode === 'realtime' ? 'Tiempo Real' : (appStore.appMode === 'file' ? 'Archivos' : 'Herramientas') }}
        </span>
      </div>

      <!-- Session Error Banner -->
      <div v-if="session.computeError && appStore.appMode !== 'tools'" class="session-error-banner">
        {{ session.computeError }}
      </div>

      <!-- SI EL MODO ES ARCHIVOS -->
      <template v-if="appStore.appMode === 'file'">
        <!-- Section PARÁMETROS -->
        <div v-if="session.hasSignals" class="section">
          <p class="section-title">PARÁMETROS</p>
          <div class="params-section">
            <div class="param-row">
              <label for="fft-size-select">FFT Size</label>
              <select id="fft-size-select" v-model.number="fftSize">
                <option :value="1024">1024</option>
                <option :value="2048">2048</option>
                <option :value="4096">4096</option>
                <option :value="8192">8192</option>
              </select>
            </div>
            <div class="param-row">
              <label for="overlap-select">Overlap</label>
              <select id="overlap-select" v-model.number="overlap">
                <option :value="0.0">0%</option>
                <option :value="0.25">25%</option>
                <option :value="0.5">50%</option>
                <option :value="0.75">75%</option>
                <option :value="0.9">90%</option>
              </select>
            </div>
            <div class="param-row">
              <label for="window-select">Ventana</label>
              <select id="window-select" v-model="windowType">
                <option value="hann">Hann</option>
                <option value="hamming">Hamming</option>
                <option value="blackman">Blackman</option>
                <option value="rectangular">Rectangular</option>
              </select>
            </div>
          </div>
        </div>
      </template>

      <!-- SI EL MODO ES TIEMPO REAL -->
      <template v-else-if="appStore.appMode === 'realtime'">
        <div class="section">
          <p class="section-title">ESTADO LIVE</p>
          <div class="live-status-card" :class="{ active: audioStore.isStreaming }">
            <div class="status-indicator">
              <span class="status-dot"></span>
              <span>{{ audioStore.isStreaming ? 'STREAMING EN VIVO' : 'ESPERANDO INICIO' }}</span>
            </div>
            <div class="live-meta-info" v-if="audioStore.isStreaming">
              <div>Frecuencia: {{ audioStore.sampleRate / 1000 }} kHz</div>
              <div>Buffer size: {{ audioStore.selectedBufferSize }} samples</div>
            </div>
          </div>
        </div>
      </template>

      <!-- Section CAPTURAS (visible en realtime y file, no en tools) -->
      <div v-if="appStore.appMode !== 'tools'" class="section">
        <p class="section-title">CAPTURAS</p>
        <div v-if="session.snapshots.length === 0" class="empty-snapshots">
          (vacío — sin capturas aún)
        </div>
        <TransitionGroup v-else name="snapshot-list" tag="div" class="snapshots-list">
          <div v-for="s in session.snapshots" :key="s.id" class="snapshot-item">
            <span
              class="dot-toggle"
              :style="{ backgroundColor: s.visible ? s.color : 'transparent', color: s.color }"
              @click="session.toggleSnapshot(s.id)"
            ></span>
            <input
              v-if="editingId === s.id"
              v-model="editingLabel"
              @blur="saveEdit(s.id)"
              @keyup.enter="saveEdit(s.id)"
              @keyup.esc="cancelEdit"
              :ref="el => { if (el) (el as HTMLInputElement).focus(); }"
              class="edit-label-input"
            />
            <span v-else @dblclick="startEdit(s)" class="snapshot-label" :title="s.label">
              {{ s.label }}
            </span>
            <button class="snapshot-delete" @click="deleteSnapshot(s.id)">✕</button>
          </div>
        </TransitionGroup>
      </div>
    </div>

    <!-- Footer -->
    <div class="footer">
      <div class="nav-item settings-btn" @click="appStore.toggleSettings()">
        <div class="settings-content">
          <IconSettings size="17" />
          <span>{{ t('sidebar.settings') }}</span>
        </div>
        <IconChevronRight size="13" class="chevron" />
      </div>
    </div>
  </div>
</template>

<style scoped>
/* DESIGN_GUIDE §1 — Core Visual Language: sidebar panel */
.sidebar {
  width: 240px;
  min-width: 240px;
  background: var(--surface-1);
  border-right: 1px solid var(--border-ghost);
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.header {
  padding: 16px;
  border-bottom: 1px solid var(--border-ghost);
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.logo {
  width: 26px;
  height: 26px;
  border-radius: var(--radius-sm);
  background: var(--accent-lime-10);
  border: 1px solid var(--border-default);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.logo-img {
  width: 14px;
  height: auto;

}

/* Varta 400, min 13px */
.title {
  font-family: var(--font-ui);
  font-size: 13px;
  font-weight: 400;
  line-height: 1.2;
  color: var(--text-white);
  letter-spacing: 0.02em;
}

.version {
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--text-gray);
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* Section label — Varta 300, small caps */
.section-title {
  font-family: var(--font-ui);
  font-size: 10px;
  font-weight: 300;
  text-transform: uppercase;
  color: var(--text-gray);
  letter-spacing: 0.09em;
  margin-bottom: 8px;
}

/* Elevated Tonal Card (DESIGN_GUIDE §6) */
.params-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
  background: var(--surface-0);
  border: 1px solid var(--border-ghost);
  border-radius: var(--radius-md);
  padding: 12px;
}

.param-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* min 13px per DESIGN_GUIDE §2-B */
.param-row label {
  font-family: var(--font-ui);
  font-size: 13px;
  font-weight: 300;
  color: var(--text-silver);
}

/* Utility control: select */
.param-row select {
  background: var(--surface-2);
  border: 1px solid var(--border-default);
  color: var(--text-white);
  border-radius: var(--radius-sm);
  padding: 3px 8px;
  font-family: var(--font-mono);
  font-size: 10px;
  outline: none;
  cursor: pointer;
}

.param-row select option {
  background-color: var(--surface-3, #1e1e21);
  color: var(--text-white, #ffffff);
}

.param-row select:focus {
  border-color: var(--border-bold);
}

.snapshots-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

/* Elevated Tonal Card item (DESIGN_GUIDE §6) */
.snapshot-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 8px;
  border-radius: var(--radius-md);
  background: var(--surface-0);
  border: 1px solid var(--border-ghost);
  position: relative;
  padding-right: 24px;
  transition: border-color 0.1s var(--ease-material);
}

.snapshot-item:hover {
  border-color: var(--border-default);
}

.dot-toggle {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  cursor: pointer;
  flex-shrink: 0;
  border: 1.5px solid currentColor;
  transition: box-shadow 0.1s var(--ease-material);
}

.dot-toggle:hover {
  box-shadow: 0 0 6px currentColor;
}

/* min 13px per DESIGN_GUIDE §2-B */
.snapshot-label {
  flex: 1;
  cursor: text;
  user-select: none;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-family: var(--font-ui);
  font-size: 13px;
  font-weight: 300;
  color: var(--text-white);
}

.edit-label-input {
  flex: 1;
  font-family: var(--font-ui);
  font-size: 13px;
  font-weight: 300;
  background: var(--surface-2);
  border: 1px solid var(--accent-lime);
  color: var(--text-white);
  border-radius: var(--radius-sm);
  padding: 0 4px;
  outline: none;
}

.snapshot-delete {
  position: absolute;
  right: 6px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: var(--text-gray);
  cursor: pointer;
  padding: 2px;
  line-height: 1;
  font-size: 11px;
  transition: color 0.1s var(--ease-material);
}

.snapshot-delete:hover {
  color: #EF4444;
}

.empty-snapshots {
  font-family: var(--font-ui);
  font-size: 13px;
  font-weight: 300;
  color: var(--text-gray);
  font-style: italic;
  padding: 4px 0;
}

.footer {
  padding: 8px;
  border-top: 1px solid var(--border-ghost);
  flex-shrink: 0;
}

/* Tactile Nav Button (DESIGN_GUIDE §5) */
.settings-btn {
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  font-family: var(--font-ui);
  font-size: 13px;
  font-weight: 300;
  color: var(--text-silver);
  padding: 8px;
  border-radius: var(--radius-md);
  transition: background 0.15s var(--ease-material), color 0.15s var(--ease-material);
}

.settings-btn:hover {
  background: var(--surface-3);
  color: var(--text-white);
}

.settings-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.chevron {
  color: var(--text-gray);
}

/* Error banner — keep red but use surface tokens */
.session-error-banner {
  padding: 8px 10px;
  background: rgba(239, 68, 68, 0.08);
  border: 1px solid rgba(239, 68, 68, 0.35);
  border-radius: var(--radius-md);
  font-family: var(--font-ui);
  font-size: 13px;
  font-weight: 300;
  color: #EF4444;
  line-height: 1.45;
  margin-bottom: 12px;
}

/* Snapshot transition */
.snapshot-list-enter-active,
.snapshot-list-leave-active {
  transition: all 0.25s var(--ease-direct);
}
.snapshot-list-enter-from {
  opacity: 0;
  transform: translateX(-10px);
}
.snapshot-list-leave-to {
  opacity: 0;
  transform: translateX(10px);
}

/* Utility Tonal Button (DESIGN_GUIDE §5) */
.back-home-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 8px 12px;
  background: var(--surface-2);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  color: var(--text-silver);
  font-family: var(--font-ui);
  font-size: 13px;
  font-weight: 300;
  cursor: pointer;
  transition: all 0.15s var(--ease-material);
  margin-bottom: 8px;
}

.back-home-btn:hover {
  background: var(--surface-3);
  border-color: var(--border-bold);
  color: var(--text-white);
}

.back-home-btn:active {
  transform: scale(0.98);
}

.mode-indicator {
  display: flex;
  justify-content: center;
  margin-bottom: 4px;
}

/* Mode pill badge — Tactile Nav Button style (DESIGN_GUIDE §5) */
.mode-badge {
  font-family: var(--font-ui);
  font-size: 10px;
  font-weight: 400;
  text-transform: uppercase;
  padding: 3px 12px;
  border-radius: var(--radius-pill);
  letter-spacing: 0.08em;
  border: 1px solid transparent;
}

.mode-badge.realtime {
  color: var(--accent-lime);
  background: var(--accent-lime-10);
  border-color: var(--border-bold);
}

.mode-badge.file {
  color: var(--accent-peach);
  background: rgba(224, 159, 103, 0.10);
  border-color: rgba(224, 159, 103, 0.3);
}

.mode-badge.tools {
  color: var(--accent-lime);
  background: var(--accent-lime-05);
  border-color: var(--border-default);
}

/* Live status card — Elevated Tonal (DESIGN_GUIDE §6) */
.live-status-card {
  background: var(--surface-0);
  border: 1px solid var(--border-ghost);
  border-radius: var(--radius-md);
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  transition: border-color 0.2s var(--ease-material);
}

.live-status-card.active {
  border-color: var(--border-bold);
  background: var(--accent-lime-05);
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.07em;
  text-transform: uppercase;
  color: var(--text-gray);
}

.live-status-card.active .status-indicator {
  color: var(--accent-lime);
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--border-default);
}

.live-status-card.active .status-dot {
  background: var(--accent-lime);
  box-shadow: 0 0 6px var(--accent-lime);
  animation: blink-dot 1.5s infinite alternate;
}

/* Live meta — JetBrains Mono for technical values (DESIGN_GUIDE §2-A) */
.live-meta-info {
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 400;
  color: var(--text-gray);
  display: flex;
  flex-direction: column;
  gap: 2px;
}

@keyframes blink-dot {
  0%   { opacity: 0.4; }
  100% { opacity: 1; }
}
</style>
