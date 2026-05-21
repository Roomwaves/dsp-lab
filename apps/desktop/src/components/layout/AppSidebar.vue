<script setup lang="ts">
import { ref, watch } from 'vue';
import { useAppStore } from '../../stores/useAppStore';
import { useMeasurementSession } from '../../stores/useMeasurementSession';
import { useI18n } from 'vue-i18n';
import { IconWaveSine, IconSettings, IconChevronRight } from '@tabler/icons-vue';

const { t } = useI18n();
const appStore = useAppStore();
const session = useMeasurementSession();

// Local dragover state
const isDragoverX = ref(false);
const isDragoverY = ref(false);

// Local upload state
const isLoadingX = ref(false);
const isLoadingY = ref(false);

// Inline errors for dropzones
const errorX = ref<string | null>(null);
const errorY = ref<string | null>(null);

// Local file sizes helper
const fileSizes = ref<{ x: string | null; y: string | null }>({ x: null, y: null });

// Refs for hidden inputs
const fileInputX = ref<HTMLInputElement | null>(null);
const fileInputY = ref<HTMLInputElement | null>(null);

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

function truncateFilename(name: string, maxLen = 22) {
  if (name.length <= maxLen) return name;
  return name.slice(0, 11) + '...' + name.slice(-8);
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
  if (slot === 'x') errorX.value = null;
  else errorY.value = null;

  if (!file.name.toLowerCase().endsWith('.wav')) {
    if (slot === 'x') errorX.value = 'Solo archivos .wav';
    else errorY.value = 'Solo archivos .wav';
    return;
  }

  try {
    if (slot === 'x') {
      isLoadingX.value = true;
      fileSizes.value.x = formatBytes(file.size);
    } else {
      isLoadingY.value = true;
      fileSizes.value.y = formatBytes(file.size);
    }
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
        <IconWaveSine size="14" class="logo-icon" />
      </div>
      <div>
        <div class="title">DSP Analyzer</div>
        <div class="version">v0.1.0</div>
      </div>
    </div>

    <!-- Sidebar content -->
    <div class="sidebar-content">
      <!-- Section SEÑALES -->
      <div class="section">
        <p class="section-title">SEÑALES</p>
        <div class="signals-container">
          <!-- Referencia X Slot -->
          <div
            class="drop-zone"
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
            <div v-if="isLoadingX" class="status-inner">
              <span class="spinner"></span>
              <span class="loading-text">Subiendo...</span>
            </div>
            <div v-else-if="session.x" class="loaded-inner">
              <div class="file-name" :title="session.x.filename">{{ truncateFilename(session.x.filename) }}</div>
              <div class="file-meta">
                X (Ref) | {{ fileSizes.x || '—' }}
              </div>
              <div class="file-meta">
                {{ formatFs(session.x.fs) }} | {{ session.x.duration.toFixed(1) }}s
              </div>
              <button class="clear-btn" @click.stop="clearSignalSlot('x')">✕</button>
            </div>
            <div v-else class="empty-inner">
              <div class="empty-title">X (Referencia)</div>
              <div class="empty-desc">Arrastrá .wav o hacé click</div>
              <div v-if="errorX" class="error-inline">{{ errorX }}</div>
            </div>
          </div>

          <!-- Medición Y Slot -->
          <div
            class="drop-zone"
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
            <div v-if="isLoadingY" class="status-inner">
              <span class="spinner"></span>
              <span class="loading-text">Subiendo...</span>
            </div>
            <div v-else-if="session.y" class="loaded-inner">
              <div class="file-name" :title="session.y.filename">{{ truncateFilename(session.y.filename) }}</div>
              <div class="file-meta">
                Y (Med) | {{ fileSizes.y || '—' }}
              </div>
              <div class="file-meta">
                {{ formatFs(session.y.fs) }} | {{ session.y.duration.toFixed(1) }}s
              </div>
              <button class="clear-btn" @click.stop="clearSignalSlot('y')">✕</button>
            </div>
            <div v-else class="empty-inner">
              <div class="empty-title">Y (Medición)</div>
              <div class="empty-desc">Arrastrá .wav o hacé click</div>
              <div v-if="errorY" class="error-inline">{{ errorY }}</div>
            </div>
          </div>
        </div>
      </div>

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

      <!-- Section CAPTURAS -->
      <div class="section">
        <p class="section-title">CAPTURAS</p>
        <div class="snapshots-list">
          <div v-if="session.snapshots.length === 0" class="empty-snapshots">
            (vacío — sin capturas aún)
          </div>
          <div v-else v-for="s in session.snapshots" :key="s.id" class="snapshot-item">
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
        </div>
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
.sidebar {
  width: 240px;
  min-width: 240px;
  background: var(--color-bg-secondary);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.header {
  padding: 16px;
  border-bottom: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.logo {
  width: 26px;
  height: 26px;
  border-radius: 7px;
  background: var(--color-accent-dim);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.logo-icon {
  color: var(--color-accent);
}

.title {
  font-size: 13px;
  font-weight: 600;
  line-height: 1.2;
  color: var(--color-text-primary);
}

.version {
  font-size: 10px;
  color: var(--color-text-secondary);
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.section-title {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--color-text-secondary);
  letter-spacing: 0.08em;
  margin-bottom: 8px;
}

.signals-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.drop-zone {
  border: 1.5px dashed var(--color-border);
  border-radius: var(--border-radius-md);
  padding: 12px;
  cursor: pointer;
  background: var(--color-bg-primary);
  transition: all 0.15s ease;
  position: relative;
  min-height: 70px;
  display: flex;
  align-items: center;
  justify-content: center;
  user-select: none;
}

.drop-zone:hover {
  border-color: var(--color-accent);
  background: var(--color-bg-elevated);
}

.drop-zone.is-dragover {
  border-color: var(--color-accent);
  background: var(--color-accent-dim);
}

.drop-zone.is-loaded {
  border-style: solid;
  border-color: var(--color-border);
  cursor: default;
}

.drop-zone.is-loaded:hover {
  background: var(--color-bg-primary);
}

.empty-inner {
  text-align: center;
}

.empty-title {
  font-size: 11px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 2px;
}

.empty-desc {
  font-size: 10px;
  color: var(--color-text-secondary);
}

.error-inline {
  font-size: 9px;
  color: #EF4444;
  margin-top: 4px;
}

.loaded-inner {
  display: flex;
  flex-direction: column;
  width: 100%;
  padding-right: 18px; /* space for clear button */
}

.file-name {
  font-size: 11px;
  font-weight: 600;
  color: var(--color-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-meta {
  font-size: 9px;
  color: var(--color-text-secondary);
  margin-top: 2px;
}

.clear-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  background: none;
  border: none;
  color: var(--color-text-secondary);
  cursor: pointer;
  font-size: 10px;
  padding: 4px;
  line-height: 1;
}

.clear-btn:hover {
  color: #EF4444;
}

.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid var(--color-border);
  border-top-color: var(--color-accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  display: inline-block;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  font-size: 10px;
  color: var(--color-text-secondary);
  margin-left: 6px;
}

.status-inner {
  display: flex;
  align-items: center;
}

.params-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-md);
  padding: 10px;
}

.param-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 11px;
}

.param-row label {
  color: var(--color-text-secondary);
}

.param-row select {
  background: var(--color-bg-elevated);
  border: 1px solid var(--color-border);
  color: var(--color-text-primary);
  border-radius: 4px;
  padding: 2px 6px;
  font-size: 10px;
  outline: none;
  cursor: pointer;
}

.param-row select:focus {
  border-color: var(--color-accent);
}

.snapshots-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.snapshot-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px;
  border-radius: var(--border-radius-md);
  font-size: 12px;
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  position: relative;
  padding-right: 24px;
}

.dot-toggle {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  cursor: pointer;
  flex-shrink: 0;
  border: 1.5px solid currentColor;
}

.snapshot-label {
  flex: 1;
  cursor: text;
  user-select: none;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 11px;
  color: var(--color-text-primary);
}

.edit-label-input {
  flex: 1;
  font-size: 11px;
  background: var(--color-bg-elevated);
  border: 1px solid var(--color-accent);
  color: var(--color-text-primary);
  border-radius: 3px;
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
  color: var(--color-text-secondary);
  cursor: pointer;
  padding: 2px;
  line-height: 1;
}

.snapshot-delete:hover {
  color: #EF4444;
}

.empty-snapshots {
  font-size: 10px;
  color: var(--color-text-secondary);
  font-style: italic;
  padding: 4px 0;
}

.footer {
  padding: 8px;
  border-top: 1px solid var(--color-border);
  flex-shrink: 0;
}

.settings-btn {
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  font-size: 12px;
  color: var(--color-text-secondary);
  padding: 8px;
  border-radius: var(--border-radius-md);
}

.settings-btn:hover {
  background: var(--color-bg-elevated);
  color: var(--color-text-primary);
}

.settings-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.chevron {
  color: var(--color-text-secondary);
}
</style>
