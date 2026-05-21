/**
 * useAudioStore — Estado global del sistema de audio.
 *
 * Sincroniza el estado Rust (vía Tauri commands + eventos) con la UI de Vue.
 *
 * ## Persistencia
 * Se persisten en localStorage:
 * - selectedInputDevice.id
 * - selectedSampleRate
 * - selectedBufferSize
 * - channelRouting
 *
 * Los dispositivos se re-enumeran en cada arranque (pueden cambiar).
 *
 * ## Eventos Tauri escuchados
 * - `audio://error`      → streamState = 'error', streamError = msg
 * - `audio://fft-result` → actualiza fftResult y currentLevel_dBFS
 */

import { defineStore } from 'pinia'
import { ref, computed, shallowRef } from 'vue'
import { invoke } from '@tauri-apps/api/core'
import { listen, type UnlistenFn } from '@tauri-apps/api/event'

import type {
  AudioDeviceInfo,
  AudioStreamConfig,
  ChannelRouting,
  FFTResult,
  StreamState,
} from '../types/audio'
import { useSignalStore } from './useSignalStore'

// ---------------------------------------------------------------------------
// Claves de localStorage
// ---------------------------------------------------------------------------
const LS_DEVICE_ID    = 'audio.deviceId'
const LS_SAMPLE_RATE  = 'audio.sampleRate'
const LS_BUFFER_SIZE  = 'audio.bufferSize'
const LS_ROUTING      = 'audio.channelRouting'

// ---------------------------------------------------------------------------
// Helpers de persistencia
// ---------------------------------------------------------------------------
function lsGet<T>(key: string, fallback: T): T {
  try {
    const raw = localStorage.getItem(key)
    return raw !== null ? (JSON.parse(raw) as T) : fallback
  } catch {
    return fallback
  }
}

function lsSet(key: string, value: unknown): void {
  try {
    localStorage.setItem(key, JSON.stringify(value))
  } catch {
    // localStorage puede no estar disponible en contexto Tauri headless
  }
}

// ---------------------------------------------------------------------------
// Store
// ---------------------------------------------------------------------------
export const useAudioStore = defineStore('audio', () => {
  const signalStore = useSignalStore()

  // ── Dispositivos ──────────────────────────────────────────────────────────
  /** Lista de dispositivos de input disponibles en el OS. */
  const inputDevices  = ref<AudioDeviceInfo[]>([])
  /** Lista de dispositivos de output disponibles en el OS. */
  const outputDevices = ref<AudioDeviceInfo[]>([])

  // ── Config activa ─────────────────────────────────────────────────────────
  /** Dispositivo de input seleccionado. */
  const selectedInputDevice = ref<AudioDeviceInfo | null>(null)
  /** Sample rate activo (Hz). */
  const selectedSampleRate  = ref<number>(lsGet(LS_SAMPLE_RATE, 44100))
  /** Tamaño de buffer (samples). */
  const selectedBufferSize  = ref<number>(lsGet(LS_BUFFER_SIZE, 512))
  /** Routing de canales activo. */
  const channelRouting = ref<ChannelRouting>(
    lsGet<ChannelRouting>(LS_ROUTING, { assignments: [], total_physical_channels: 0 })
  )

  // ── Estado del stream ─────────────────────────────────────────────────────
  const streamState = ref<StreamState>('stopped')
  const streamError = ref<string | null>(null)
  const isLoading   = ref(false)

  // ── RTA (mantiene compatibilidad con el código anterior) ──────────────────
  /** @deprecated Usar streamState en su lugar para el estado real del stream. */
  const isStreaming = computed(() => streamState.value === 'running')

  // ── Métricas en vivo ──────────────────────────────────────────────────────
  /** Nivel RMS del último bloque en dBFS. */
  const currentLevel_dBFS = ref<number>(-Infinity)
  /** Último resultado de FFT recibido del processing thread. */
  const fftResult = shallowRef<FFTResult | null>(null)

  // ── Computed ──────────────────────────────────────────────────────────────
  /** Latencia estimada en ms según buffer size y sample rate. */
  const estimatedLatencyMs = computed(() =>
    (selectedBufferSize.value / selectedSampleRate.value) * 1000
  )

  // Compat con código anterior que usa latencyEstimateMs
  const latencyEstimateMs = estimatedLatencyMs

  // ── Listeners Tauri (se inicializan una sola vez) ─────────────────────────
  const _unlisteners: UnlistenFn[] = []

  // ── Acciones ──────────────────────────────────────────────────────────────

  /**
   * Enumera los dispositivos de audio disponibles en el OS.
   * Invoca `get_input_devices` y `get_output_devices` en paralelo.
   * Restaura el dispositivo seleccionado desde localStorage si existe.
   */
  async function loadDevices(): Promise<void> {
    isLoading.value = true
    streamError.value = null
    try {
      const [inputs, outputs] = await Promise.all([
        invoke<AudioDeviceInfo[]>('get_input_devices'),
        invoke<AudioDeviceInfo[]>('get_output_devices'),
      ])
      inputDevices.value  = inputs
      outputDevices.value = outputs

      // Restaurar selección persistida
      const savedId = lsGet<string | null>(LS_DEVICE_ID, null)
      if (savedId) {
        selectedInputDevice.value = inputs.find(d => d.id === savedId) ?? inputs[0] ?? null
      } else {
        selectedInputDevice.value = inputs.find(d => d.is_default) ?? inputs[0] ?? null
      }
    } catch (err) {
      streamError.value = (err as Error).message ?? String(err)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Abre el stream de audio con la configuración activa.
   * Si ya hay un stream activo, lo cierra primero (invariante de unicidad
   * aplicado en Rust).
   */
  async function startStream(): Promise<void> {
    if (!selectedInputDevice.value) {
      streamError.value = 'No hay dispositivo de input seleccionado'
      return
    }

    isLoading.value = true
    streamError.value = null

    const config: AudioStreamConfig = {
      device_id:   selectedInputDevice.value.id,
      sample_rate: selectedSampleRate.value,
      channels:    _effectiveChannels(),
      buffer_size: selectedBufferSize.value,
    }

    try {
      await invoke('start_audio_stream', { config })
      streamState.value = 'running'
      _persistConfig()
    } catch (err) {
      streamState.value = 'error'
      streamError.value = (err as Error).message ?? String(err)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Cierra el stream activo de forma ordenada.
   */
  async function stopStream(): Promise<void> {
    isLoading.value = true
    try {
      await invoke('stop_audio_stream')
      streamState.value = 'stopped'
      streamError.value = null
    } catch (err) {
      streamError.value = (err as Error).message ?? String(err)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Detiene el stream actual, aplica la nueva config y lo reinicia.
   * Útil cuando el usuario cambia sample rate o buffer size mientras está activo.
   */
  async function applyConfig(): Promise<void> {
    await stopStream()
    await startStream()
  }

  /**
   * Aplica un nuevo routing de canales.
   * El cambio toma efecto en el próximo bloque procesado (sin reiniciar el stream).
   */
  async function applyChannelRouting(routing: ChannelRouting): Promise<void> {
    try {
      await invoke('set_channel_routing', { routing })
      channelRouting.value = routing
      lsSet(LS_ROUTING, routing)
    } catch (err) {
      streamError.value = (err as Error).message ?? String(err)
    }
  }

  /**
   * Suscribe a los eventos Tauri de audio.
   * Llamar una sola vez al montar la app principal (ej. en App.vue).
   * Los listeners se limpian automáticamente al llamar `cleanup()`.
   */
  async function listenToStreamEvents(): Promise<void> {
    // Evitar registrar listeners duplicados
    if (_unlisteners.length > 0) return

    const unlistenError = await listen<string>('audio://error', (event) => {
      streamState.value = 'error'
      streamError.value = event.payload
    })

    const unlistenFFT = await listen<FFTResult>('audio://fft-result', (event) => {
      const result = event.payload
      fftResult.value          = result
      currentLevel_dBFS.value  = result.level_dbfs

      // Actualizar signalStore para que RTAView y otros lo consuman
      signalStore.frequencies   = result.frequencies
      signalStore.fftMagnitudes = result.magnitudes_db
    })

    _unlisteners.push(unlistenError, unlistenFFT)
  }

  /**
   * Limpia los listeners Tauri. Llamar al desmontar la app.
   */
  function cleanup(): void {
    _unlisteners.forEach(fn => fn())
    _unlisteners.length = 0
  }

  // ── Sync polling (compat con código anterior) ─────────────────────────────
  // Mantiene la API de startStream/stopStream síncrona que usaba RTAView.
  // El stream real ahora viene de CPAL; esta función es un no-op cuando
  // el stream Tauri está activo.

  /** @deprecated Usar startStream() async en su lugar. */
  function startStreamSync(): void {
    startStream().catch(console.error)
  }

  /** @deprecated Usar stopStream() async en su lugar. */
  function stopStreamSync(): void {
    stopStream().catch(console.error)
  }

  // ── Helpers internos ──────────────────────────────────────────────────────

  /** Determina cuántos canales abrir basándose en el routing configurado. */
  function _effectiveChannels(): number {
    if (channelRouting.value.total_physical_channels > 0) {
      return channelRouting.value.total_physical_channels
    }
    // Fallback: abrir el mínimo soportado por el dispositivo (usualmente 1 o 2)
    const configs = selectedInputDevice.value?.supported_configs ?? []
    return configs[0]?.channels ?? 1
  }

  /** Persiste la configuración activa en localStorage. */
  function _persistConfig(): void {
    if (selectedInputDevice.value) {
      lsSet(LS_DEVICE_ID, selectedInputDevice.value.id)
    }
    lsSet(LS_SAMPLE_RATE, selectedSampleRate.value)
    lsSet(LS_BUFFER_SIZE, selectedBufferSize.value)
  }

  // ── Retorno del store ─────────────────────────────────────────────────────
  return {
    // Dispositivos
    inputDevices,
    outputDevices,
    // Config activa
    selectedInputDevice,
    selectedSampleRate,
    selectedBufferSize,
    channelRouting,
    // Estado del stream
    streamState,
    streamError,
    isLoading,
    // Compat
    isStreaming,
    /** @deprecated Usar selectedInputDevice */
    selectedInput: computed(() => selectedInputDevice.value?.id ?? ''),
    /** @deprecated Usar selectedSampleRate */
    sampleRate: selectedSampleRate,
    /** @deprecated Usar selectedBufferSize */
    bufferSize: selectedBufferSize,
    // Métricas
    currentLevel_dBFS,
    fftResult,
    estimatedLatencyMs,
    latencyEstimateMs,
    // Acciones
    loadDevices,
    startStream,
    stopStream,
    applyConfig,
    applyChannelRouting,
    listenToStreamEvents,
    cleanup,
    // Compat (síncrono → async)
    startStreamSync,
    stopStreamSync,
    // RTA legacy (fftSize, windowType, avgMode los mantiene RTAView localmente)
  }
})
