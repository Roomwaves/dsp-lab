<script setup lang="ts">
import { computed, onMounted } from 'vue';
import { storeToRefs } from 'pinia';
import { useAudioStore } from '../../stores/useAudioStore';
import { 
  IconPlayerPlay, 
  IconRefresh, 
  IconAlertTriangle, 
  IconSettings
} from '@tabler/icons-vue';
import type { ChannelRouting } from '../../types/audio';

const audioStore = useAudioStore();

const { 
  inputDevices, 
  selectedInputDevice,
  selectedSampleRate, 
  selectedBufferSize, 
  supportedSampleRates,
  supportedBufferSizes,
  estimatedLatencyMs,
  validationError,
  streamError,
  isLoading,
  channelRouting
} = storeToRefs(audioStore);

const selectedDeviceId = computed({
  get: () => selectedInputDevice.value?.id ?? '',
  set: (id: string) => {
    const dev = inputDevices.value.find(d => d.id === id);
    if (dev) {
      selectedInputDevice.value = dev;
    }
  }
});

const availableChannels = computed(() => {
  const total = channelRouting.value.total_physical_channels || 2;
  const channels: number[] = [];
  for (let i = 0; i < total; i++) {
    channels.push(i);
  }
  return channels;
});

const channelXPhysical = computed({
  get: () => {
    const assignment = channelRouting.value.assignments.find(
      a => a.logical_name === 'X (input)' || a.logical_name.startsWith('X')
    );
    return assignment ? assignment.physical_channel : 0;
  },
  set: (val: number) => {
    const routing = JSON.parse(JSON.stringify(channelRouting.value)) as ChannelRouting;
    const assignment = routing.assignments.find(
      a => a.logical_name === 'X (input)' || a.logical_name.startsWith('X')
    );
    if (assignment) {
      assignment.physical_channel = val;
    } else {
      routing.assignments.push({ logical_name: 'X (input)', physical_channel: val });
    }
    audioStore.applyChannelRouting(routing);
  }
});

const channelYPhysical = computed({
  get: () => {
    const assignment = channelRouting.value.assignments.find(
      a => a.logical_name === 'Y (output)' || a.logical_name.startsWith('Y')
    );
    return assignment ? assignment.physical_channel : 1;
  },
  set: (val: number) => {
    const routing = JSON.parse(JSON.stringify(channelRouting.value)) as ChannelRouting;
    const assignment = routing.assignments.find(
      a => a.logical_name === 'Y (output)' || a.logical_name.startsWith('Y')
    );
    if (assignment) {
      assignment.physical_channel = val;
    } else {
      routing.assignments.push({ logical_name: 'Y (output)', physical_channel: val });
    }
    audioStore.applyChannelRouting(routing);
  }
});

function handleStart() {
  audioStore.startStream();
}

onMounted(() => {
  // Asegurar que carguen los dispositivos si la lista está vacía
  if (inputDevices.value.length === 0) {
    audioStore.loadDevices();
  }
});
</script>

<template>
  <div class="io-setup-container">
    <div class="glass-card io-setup-card">
      <div class="setup-header">
        <div class="logo-badge">
          <IconSettings size="22" class="badge-icon" />
        </div>
        <h2 class="title">Configuración de Entrada/Salida</h2>
        <p class="subtitle">Ajustá la interfaz de audio, la frecuencia y la correspondencia lógica de canales para comenzar la medición.</p>
      </div>

      <div class="setup-body">
        <!-- Dispositivo -->
        <div class="form-section">
          <label class="section-title">Interfaz de Audio</label>
          <div class="custom-select-wrapper">
            <select v-model="selectedDeviceId" class="sleek-select">
              <option v-if="inputDevices.length === 0" value="">Buscando dispositivos...</option>
              <option v-for="dev in inputDevices" :key="dev.id" :value="dev.id">
                {{ dev.name }} {{ dev.is_default ? '(Predeterminado)' : '' }}
              </option>
            </select>
          </div>
        </div>

        <!-- Frecuencia y Buffer -->
        <div class="form-row">
          <div class="form-section flex-1">
            <label class="section-title">Frecuencia de Muestreo</label>
            <div class="custom-select-wrapper">
              <select v-model="selectedSampleRate" class="sleek-select">
                <option v-for="rate in supportedSampleRates" :key="rate" :value="rate">
                  {{ rate / 1000 }} kHz
                </option>
              </select>
            </div>
          </div>

          <div class="form-section flex-1">
            <label class="section-title">Tamaño del Buffer</label>
            <div class="custom-select-wrapper">
              <select v-model="selectedBufferSize" class="sleek-select">
                <option v-for="sz in supportedBufferSizes" :key="sz" :value="sz">
                  {{ sz }} samples
                </option>
              </select>
            </div>
            <div class="helper-info">
              Latencia estimada: <strong>{{ estimatedLatencyMs.toFixed(1) }} ms</strong>
            </div>
          </div>
        </div>

        <!-- Mapeo de Canales Lógicos -->
        <div class="form-row">
          <div class="form-section flex-1">
            <label class="section-title">Canal de Referencia (X)</label>
            <div class="custom-select-wrapper select-x-wrapper">
              <select v-model="channelXPhysical" class="sleek-select">
                <option v-for="ch in availableChannels" :key="ch" :value="ch">
                  Entrada {{ ch + 1 }}
                </option>
              </select>
            </div>
            <div class="helper-info">
              Canal para señal de loopback/referencia
            </div>
          </div>

          <div class="form-section flex-1">
            <label class="section-title">Canal de Medición (Y)</label>
            <div class="custom-select-wrapper select-y-wrapper">
              <select v-model="channelYPhysical" class="sleek-select">
                <option v-for="ch in availableChannels" :key="ch" :value="ch">
                  Entrada {{ ch + 1 }}
                </option>
              </select>
            </div>
            <div class="helper-info">
              Canal para señal capturada/micrófono
            </div>
          </div>
        </div>

        <!-- Alert messages -->
        <div v-if="validationError" class="alert-box warning-alert">
          <IconAlertTriangle size="18" class="alert-icon" />
          <div class="alert-content">
            <span class="alert-title">Configuración inválida</span>
            <span class="alert-desc">{{ validationError }}</span>
          </div>
        </div>

        <div v-if="streamError" class="alert-box error-alert">
          <IconAlertTriangle size="18" class="alert-icon" />
          <div class="alert-content">
            <span class="alert-title">Error del Stream</span>
            <span class="alert-desc">{{ streamError }}</span>
          </div>
        </div>

        <!-- Start Button -->
        <button 
          @click="handleStart" 
          class="btn-start-stream" 
          :disabled="isLoading || !!validationError"
        >
          <IconRefresh v-if="isLoading" class="spin-icon" size="18" />
          <IconPlayerPlay v-else size="18" />
          <span>{{ isLoading ? 'Inicializando Motor...' : 'Iniciar Motor DSP' }}</span>
        </button>

        <!-- Simulation Option -->
        <div class="simulation-section">
          <div class="divider-text">o bien</div>
          <button 
            @click="audioStore.startSimulation()" 
            class="btn-start-simulation"
            type="button"
          >
            <IconPlayerPlay size="16" />
            <span>Simular Entrada (Demo sin hardware)</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.io-setup-container {
  display: flex;
  justify-content: center;
  align-items: center;
  flex: 1;
  padding: 40px 20px;
  background-color: var(--color-bg-primary);
  min-height: 0;
  overflow-y: auto;
}

.io-setup-card {
  width: 100%;
  max-width: 600px;
  border-radius: var(--border-radius-lg);
  padding: 32px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.glass-card {
  background: rgba(24, 28, 36, 0.65);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.io-setup-card:hover {
  border-color: rgba(0, 217, 126, 0.15);
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.5), 0 0 24px rgba(0, 217, 126, 0.03);
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
  animation: float 4s ease-in-out infinite;
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

.form-row {
  display: flex;
  gap: 16px;
}

.flex-1 {
  flex: 1;
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.section-title {
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  color: var(--color-text-secondary);
}

.custom-select-wrapper {
  position: relative;
  width: 100%;
}

.sleek-select {
  width: 100%;
  padding: 11px 16px;
  background: rgba(16, 18, 23, 0.6);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-md);
  color: var(--color-text-primary);
  font-size: 13px;
  font-family: inherit;
  outline: none;
  cursor: pointer;
  appearance: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.sleek-select option {
  background-color: var(--surface-3, #1e1e21);
  color: var(--text-white, #ffffff);
}

.sleek-select:focus {
  border-color: var(--color-accent);
  box-shadow: 0 0 0 2px var(--color-accent-dim);
}

.custom-select-wrapper::after {
  content: '↓';
  position: absolute;
  right: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--color-text-secondary);
  font-size: 10px;
  pointer-events: none;
  opacity: 0.7;
}

.helper-info {
  font-size: 11px;
  color: var(--color-text-secondary);
  margin-top: 4px;
}

.helper-info strong {
  color: var(--color-accent);
}

/* Color accents for channel selectors */
.select-x-wrapper select:focus {
  border-color: var(--color-accent);
  box-shadow: 0 0 0 2px var(--color-accent-dim);
}

.select-y-wrapper select:focus {
  border-color: #818cf8;
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.15);
}

/* Alerts */
.alert-box {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 16px;
  border-radius: var(--border-radius-md);
  font-size: 12px;
  line-height: 1.4;
  border: 1px solid transparent;
}

.warning-alert {
  background: rgba(245, 158, 11, 0.08);
  border-color: rgba(245, 158, 11, 0.2);
  color: #fbbf24;
}

.error-alert {
  background: rgba(239, 68, 68, 0.08);
  border-color: rgba(239, 68, 68, 0.2);
  color: #f87171;
}

.alert-icon {
  margin-top: 2px;
  flex-shrink: 0;
}

.alert-content {
  display: flex;
  flex-direction: column;
}

.alert-title {
  font-weight: 600;
  margin-bottom: 2px;
}

.alert-desc {
  opacity: 0.9;
}

/* Button */
.btn-start-stream {
  width: 100%;
  padding: 12px 24px;
  background: linear-gradient(135deg, var(--color-accent), #00b368);
  border: none;
  border-radius: var(--border-radius-md);
  color: #050505;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 12px rgba(0, 217, 126, 0.2);
}

.btn-start-stream:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 18px rgba(0, 217, 126, 0.35);
  background: linear-gradient(135deg, #05e687, var(--color-accent));
}

.btn-start-stream:active:not(:disabled) {
  transform: translateY(1px);
  box-shadow: 0 2px 6px rgba(0, 217, 126, 0.2);
}

.btn-start-stream:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  box-shadow: none;
}

.spin-icon {
  animation: spin 1s infinite linear;
}

/* Keyframes */
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-4px); }
}

@keyframes spin {
  100% { transform: rotate(360deg); }
}

@keyframes pulse-flow {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

.simulation-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  margin-top: 8px;
  width: 100%;
}

.divider-text {
  font-size: 10px;
  font-weight: 600;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 1px;
  opacity: 0.5;
  display: flex;
  align-items: center;
  width: 100%;
}

.divider-text::before,
.divider-text::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--color-border);
  margin: 0 10px;
}

.btn-start-simulation {
  width: 100%;
  padding: 12px 24px;
  background: rgba(129, 140, 248, 0.08);
  border: 1px dashed rgba(129, 140, 248, 0.3);
  border-radius: var(--border-radius-md);
  color: #a5b4fc;
  font-weight: 600;
  font-size: 13px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.2s ease;
}

.btn-start-simulation:hover {
  background: rgba(129, 140, 248, 0.16);
  border-color: #818cf8;
  color: #c7d2fe;
  box-shadow: 0 4px 12px rgba(129, 140, 248, 0.1);
}

.btn-start-simulation:active {
  transform: scale(0.99);
}
</style>
