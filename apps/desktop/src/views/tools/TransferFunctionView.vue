<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import { ref, computed } from 'vue';
import { IconUpload, IconPlayerPlay } from '@tabler/icons-vue';
import { api } from '../../services/api';
import FrequencyResponsePlot from '../../components/plots/FrequencyResponsePlot.vue';
import type { FrequencyResponseOutput } from '../../types/dsp';

const { t } = useI18n();

// Canales de entrada
const ch1File = ref<File | null>(null);
const ch2File = ref<File | null>(null);
const ch1Samples = ref<number[]>([]);
const ch2Samples = ref<number[]>([]);
const fs = ref(44100);
const averages = ref(8);
const avgOptions = [1, 4, 8, 16, 32];

// Estado
const isLoading = ref(false);
const error = ref<string | null>(null);

// Resultado H(ω)
const result = ref<FrequencyResponseOutput | null>(null);

const frequencies = computed(() => result.value?.frequencies ?? []);
const magnitudeDb = computed(() => result.value?.magnitude_db ?? []);
const phaseRad = computed(() => result.value?.phase_rad ?? []);
const hasResult = computed(() => frequencies.value.length > 0);

async function readWav(file: File): Promise<number[]> {
  // Lee el archivo como ArrayBuffer y lo decodifica con la Web Audio API
  const ctx = new OfflineAudioContext(1, 1, 44100);
  const buffer = await file.arrayBuffer();
  const decoded = await ctx.decodeAudioData(buffer);
  fs.value = decoded.sampleRate;
  return Array.from(decoded.getChannelData(0));
}

async function onCh1Change(e: Event) {
  const f = (e.target as HTMLInputElement).files?.[0];
  if (!f) return;
  ch1File.value = f;
  ch1Samples.value = await readWav(f);
}

async function onCh2Change(e: Event) {
  const f = (e.target as HTMLInputElement).files?.[0];
  if (!f) return;
  ch2File.value = f;
  ch2Samples.value = await readWav(f);
}

async function compute() {
  if (ch1Samples.value.length === 0 || ch2Samples.value.length === 0) return;
  isLoading.value = true;
  error.value = null;
  try {
    result.value = await api.frequencyResponse(ch1Samples.value, ch2Samples.value, fs.value);
  } catch (e) {
    error.value = (e as Error).message;
  } finally {
    isLoading.value = false;
  }
}

const ch1Label = computed(() => ch1File.value?.name ?? t('controls.input') + ' (CH1 · X)');
const ch2Label = computed(() => ch2File.value?.name ?? t('controls.output') + ' (CH2 · Y)');
</script>

<template>
  <div class="tf-view">
    <!-- TopBar -->
    <div class="tf-topbar">
      <span class="tf-title">{{ t('sidebar.transfer_function') }}</span>
      <span class="tf-subtitle">H(ω) = Y(ω) / X(ω)</span>
    </div>

    <!-- Channel inputs -->
    <div class="channels-row">
      <label class="channel-card" for="tf-ch1-input">
        <div class="ch-badge">CH1 · X</div>
        <div class="ch-filename">{{ ch1Label }}</div>
        <div class="ch-action">
          <IconUpload size="13" />
          <span>{{ t('controls.load') ?? 'Load .wav' }}</span>
        </div>
        <input id="tf-ch1-input" type="file" accept=".wav" class="file-input" @change="onCh1Change" />
      </label>

      <div class="arrow-divider">→</div>

      <label class="channel-card" for="tf-ch2-input">
        <div class="ch-badge ch2">CH2 · Y</div>
        <div class="ch-filename">{{ ch2Label }}</div>
        <div class="ch-action">
          <IconUpload size="13" />
          <span>{{ t('controls.load') ?? 'Load .wav' }}</span>
        </div>
        <input id="tf-ch2-input" type="file" accept=".wav" class="file-input" @change="onCh2Change" />
      </label>
    </div>

    <!-- Controls -->
    <div class="controls-row">
      <div class="control-group">
        <span class="ctrl-label">Avg:</span>
        <button
          v-for="a in avgOptions"
          :key="a"
          class="pill-btn"
          :class="{ active: averages === a }"
          @click="averages = a"
        >{{ a }}</button>
      </div>

      <button
        id="tf-compute-btn"
        class="btn btn-primary"
        :disabled="isLoading || ch1Samples.length === 0 || ch2Samples.length === 0"
        @click="compute"
      >
        <IconPlayerPlay size="13" />
        {{ isLoading ? t('status.computing') ?? 'Computing…' : t('controls.compute') ?? 'Compute H(ω)' }}
      </button>
    </div>

    <!-- Error -->
    <div v-if="error" class="error-banner">{{ error }}</div>

    <!-- Plot -->
    <div class="plot-area">
      <FrequencyResponsePlot
        v-if="hasResult"
        id="tf-fr-plot"
        :frequencies="frequencies"
        :magnitud-db="magnitudeDb"
        :phase-rad="phaseRad"
        :height="0"
        class="fr-fill"
      />
      <div v-else class="empty-state">
        <span>{{ t('status.ready') }} — cargá CH1 y CH2, luego calculá H(ω)</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.tf-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  overflow: hidden;
}

.tf-topbar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 20px;
  border-bottom: 0.5px solid var(--color-border);
  flex-shrink: 0;
}

.tf-title {
  font-size: 13px;
  font-weight: 600;
}

.tf-subtitle {
  font-size: 11px;
  font-family: var(--font-mono);
  color: var(--color-text-secondary);
}

/* Channels */
.channels-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 20px;
  flex-shrink: 0;
}

.channel-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 14px 16px;
  background: var(--color-bg-secondary);
  border: 0.5px solid var(--color-border);
  border-radius: var(--border-radius-md);
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
  position: relative;
}

.channel-card:hover {
  border-color: var(--color-accent);
  background: var(--color-bg-elevated);
}

.file-input {
  position: absolute;
  inset: 0;
  opacity: 0;
  cursor: pointer;
  width: 100%;
  height: 100%;
}

.ch-badge {
  font-size: 10px;
  font-weight: 700;
  color: var(--color-accent);
  background: var(--color-accent-dim, rgba(0, 217, 126, 0.12));
  padding: 2px 6px;
  border-radius: 4px;
  width: fit-content;
}

.ch-badge.ch2 {
  color: #3B82F6;
  background: rgba(59, 130, 246, 0.12);
}

.ch-filename {
  font-size: 11px;
  color: var(--color-text-primary);
  font-family: var(--font-mono);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.ch-action {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 11px;
  color: var(--color-text-tertiary);
}

.arrow-divider {
  font-size: 18px;
  color: var(--color-text-tertiary);
  flex-shrink: 0;
}

/* Controls */
.controls-row {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 8px 20px 14px;
  flex-shrink: 0;
}

.control-group {
  display: flex;
  align-items: center;
  gap: 6px;
}

.ctrl-label {
  font-size: 11px;
  color: var(--color-text-secondary);
  font-weight: 500;
}

.pill-btn {
  padding: 4px 10px;
  border-radius: 20px;
  border: 0.5px solid var(--color-border);
  background: var(--color-bg-secondary);
  color: var(--color-text-secondary);
  font-size: 11px;
  font-family: var(--font-mono);
  cursor: pointer;
  transition: background 0.12s, color 0.12s, border-color 0.12s;
}

.pill-btn.active {
  background: var(--color-accent-dim, rgba(0, 217, 126, 0.12));
  color: var(--color-accent);
  border-color: var(--color-accent);
}

.btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 16px;
  border-radius: var(--border-radius-md);
  font-size: 12px;
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition: opacity 0.15s;
}

.btn:disabled {
  opacity: 0.38;
  cursor: not-allowed;
}

.btn-primary {
  background: var(--color-accent);
  color: #fff;
  margin-left: auto;
}

/* Error */
.error-banner {
  margin: 0 20px;
  padding: 8px 12px;
  background: rgba(239, 68, 68, 0.1);
  border: 0.5px solid rgba(239, 68, 68, 0.4);
  border-radius: var(--border-radius-md);
  font-size: 12px;
  color: #EF4444;
  flex-shrink: 0;
}

/* Plot */
.plot-area {
  flex: 1;
  position: relative;
  overflow: hidden;
  padding: 0 16px 16px;
}

.fr-fill {
  height: 100% !important;
}

.plot-area :deep(.fr-container) {
  height: 100% !important;
}

.empty-state {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: var(--color-text-tertiary);
}
</style>
