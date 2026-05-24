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
 * - `audio://error`              → streamState = 'error', streamError = msg
 * - `audio://fft-result`         → actualiza fftResult y currentLevel_dBFS
 * - `audio://device-connected`   → añade dispositivo a inputDevices
 * - `audio://device-disconnected`→ elimina dispositivo; si era el activo, marca error
 * - `audio://output-connected`   → añade dispositivo a outputDevices
 * - `audio://output-disconnected`→ elimina dispositivo de outputDevices
 */

import { defineStore } from 'pinia'
import { ref, computed, shallowRef, watch } from 'vue'
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

export type FftSize = 1024 | 2048 | 4096
export type WindowType = 'hann' | 'hamming' | 'blackman' | 'rectangular'
export type AvgMode = 'off' | 8 | 16

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
  /** Dispositivo de output seleccionado. */
  const selectedOutputDevice = ref<AudioDeviceInfo | null>(null)
  /** Sample rate activo (Hz). */
  const selectedSampleRate  = ref<number>(lsGet(LS_SAMPLE_RATE, 44100))
  /** Tamaño de buffer (samples). */
  const selectedBufferSize  = ref<number>(lsGet(LS_BUFFER_SIZE, 512))

  // ── RTA Config ────────────────────────────────────────────────────────────
  const fftSize = ref<FftSize>(2048)
  const windowType = ref<WindowType>('hann')
  const avgMode = ref<AvgMode>('off')

  // ── Validación (#48) ──────────────────────────────────────────────────────
  /** Error de validación de config (sample rate/canales/buffer incompatibles). */
  const validationError = ref<string | null>(null)
  /** Sample rates soportados por el dispositivo seleccionado actualmente. */
  const supportedSampleRates = ref<number[]>([])
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

  /** Nivel RMS del canal lógico X (Reference) en dBFS. */
  const levelX_dBFS = computed(() => {
    if (!fftResult.value || !fftResult.value.channel_levels_dbfs) return -Infinity
    const assignment = channelRouting.value.assignments.find(
      a => a.logical_name === 'X (input)' || a.logical_name.startsWith('X')
    )
    if (!assignment) return -Infinity
    const idx = assignment.physical_channel
    if (idx < 0 || idx >= fftResult.value.channel_levels_dbfs.length) return -Infinity
    return fftResult.value.channel_levels_dbfs[idx]
  })

  /** Nivel RMS del canal lógico Y (Measurement) en dBFS. */
  const levelY_dBFS = computed(() => {
    if (!fftResult.value || !fftResult.value.channel_levels_dbfs) return -Infinity
    const assignment = channelRouting.value.assignments.find(
      a => a.logical_name === 'Y (output)' || a.logical_name.startsWith('Y')
    )
    if (!assignment) return -Infinity
    const idx = assignment.physical_channel
    if (idx < 0 || idx >= fftResult.value.channel_levels_dbfs.length) return -Infinity
    return fftResult.value.channel_levels_dbfs[idx]
  })

  // ── Computed ──────────────────────────────────────────────────────────────
  /** Latencia estimada en ms según buffer size y sample rate. */
  const estimatedLatencyMs = computed(() =>
    (selectedBufferSize.value / selectedSampleRate.value) * 1000
  )

  // Compat con código anterior que usa latencyEstimateMs
  const latencyEstimateMs = estimatedLatencyMs

  /** Buffer sizes soportados por el dispositivo seleccionado actualmente. */
  const supportedBufferSizes = computed(() => {
    const dev = selectedInputDevice.value
    if (!dev) return [128, 256, 512, 1024, 2048]
    
    // Buscar configs que soporten el sample rate actual
    const matchingConfigs = dev.supported_configs.filter(c => 
      selectedSampleRate.value >= c.min_sample_rate && 
      selectedSampleRate.value <= c.max_sample_rate
    )
    
    const configsToUse = matchingConfigs.length > 0 ? matchingConfigs : dev.supported_configs
    
    let min = 0
    let max = Infinity
    let hasRange = false
    
    for (const c of configsToUse) {
      if (c.buffer_size_range) {
        min = Math.max(min, c.buffer_size_range[0])
        max = Math.min(max, c.buffer_size_range[1])
        hasRange = true
      }
    }
    
    const candidates = [64, 128, 256, 512, 1024, 2048, 4096, 8192]
    if (hasRange) {
      const filtered = candidates.filter(sz => sz >= min && sz <= max)
      if (filtered.length === 0) {
        const result: number[] = []
        for (const sz of candidates) {
          if (sz >= min && sz <= max) result.push(sz)
        }
        if (result.length === 0) {
          if (min > 0) result.push(min)
          if (max < Infinity && max > min) result.push(max)
        }
        return result.length > 0 ? result : [256, 512, 1024]
      }
      return filtered
    }
    
    return [128, 256, 512, 1024, 2048]
  })

  // Watch buffer sizes soportados para ajustar el buffer size activo si queda fuera de rango
  watch(supportedBufferSizes, (newSizes) => {
    if (newSizes.length > 0 && !newSizes.includes(selectedBufferSize.value)) {
      if (newSizes.includes(512)) {
        selectedBufferSize.value = 512
      } else {
        selectedBufferSize.value = newSizes[0]
      }
    }
  }, { immediate: true })

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

      // Restaurar selección de input persistida
      const savedId = lsGet<string | null>(LS_DEVICE_ID, null)
      if (savedId) {
        selectedInputDevice.value = inputs.find(d => d.id === savedId) ?? inputs[0] ?? null
      } else {
        selectedInputDevice.value = inputs.find(d => d.is_default) ?? inputs[0] ?? null
      }

      // Restaurar selección de output persistida
      const savedOutputId = lsGet<string | null>('audio.outputDeviceId', null)
      if (savedOutputId) {
        selectedOutputDevice.value = outputs.find(d => d.id === savedOutputId) ?? outputs[0] ?? null
      } else {
        selectedOutputDevice.value = outputs.find(d => d.is_default) ?? outputs[0] ?? null
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

    // ── Hot-plug (#47) ────────────────────────────────────────────────────
    const unlistenDevConn = await listen<AudioDeviceInfo>('audio://device-connected', (event) => {
      const device = event.payload
      // Añadir si no existe ya (evitar duplicados en caso de re-enumeración)
      if (!inputDevices.value.some(d => d.id === device.id)) {
        inputDevices.value = [...inputDevices.value, device]
      }
    })

    const unlistenDevDisc = await listen<AudioDeviceInfo>('audio://device-disconnected', (event) => {
      const device = event.payload
      inputDevices.value = inputDevices.value.filter(d => d.id !== device.id)

      // Si era el dispositivo activo, marcar error de stream
      if (selectedInputDevice.value?.id === device.id) {
        streamState.value = 'error'
        streamError.value = `El dispositivo de audio "${device.name}" se desconectó.`
        selectedInputDevice.value = null
      }
    })

    const unlistenOutConn = await listen<AudioDeviceInfo>('audio://output-connected', (event) => {
      const device = event.payload
      if (!outputDevices.value.some(d => d.id === device.id)) {
        outputDevices.value = [...outputDevices.value, device]
      }
    })

    const unlistenOutDisc = await listen<AudioDeviceInfo>('audio://output-disconnected', (event) => {
      const device = event.payload
      outputDevices.value = outputDevices.value.filter(d => d.id !== device.id)
    })

    _unlisteners.push(
      unlistenError, unlistenFFT,
      unlistenDevConn, unlistenDevDisc,
      unlistenOutConn, unlistenOutDisc,
    )
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

  /**
   * Carga los sample rates soportados por el dispositivo actualmente seleccionado.
   * Llamar cada vez que cambia `selectedInputDevice`.
   */
  async function loadSupportedSampleRates(): Promise<void> {
    if (!selectedInputDevice.value) {
      supportedSampleRates.value = []
      return
    }
    try {
      supportedSampleRates.value = await invoke<number[]>(
        'get_supported_sample_rates',
        { deviceId: selectedInputDevice.value.id },
      )
    } catch {
      // Fallback: lista global de rates comunes si el comando falla
      supportedSampleRates.value = [44100, 48000, 96000]
    }
  }

  /**
   * Valida la configuración activa contra las capacidades del dispositivo.
   * Actualiza `validationError` con el mensaje de error o null si es válida.
   */
  async function validateConfig(): Promise<boolean> {
    if (!selectedInputDevice.value) {
      validationError.value = 'No hay dispositivo seleccionado'
      return false
    }
    try {
      await invoke('validate_audio_config', {
        deviceId: selectedInputDevice.value.id,
        config: {
          device_id:   selectedInputDevice.value.id,
          sample_rate: selectedSampleRate.value,
          channels:    _effectiveChannels(),
          buffer_size: selectedBufferSize.value,
        },
      })
      validationError.value = null
      return true
    } catch (err) {
      validationError.value = (err as Error).message ?? String(err)
      return false
    }
  }

  // Watch input device changes to automatically update supported rates and validation
  watch(selectedInputDevice, async (newDev) => {
    if (newDev) {
      await loadSupportedSampleRates()
      
      // Auto routing mapping logic
      const totalChannels = newDev.supported_configs.length > 0
        ? Math.max(...newDev.supported_configs.map(c => c.channels))
        : 2
      
      const assignments = [
        { logical_name: 'X (input)', physical_channel: 0 }
      ]
      if (totalChannels >= 2) {
        assignments.push({ logical_name: 'Y (output)', physical_channel: 1 })
      } else {
        assignments.push({ logical_name: 'Y (output)', physical_channel: 0 })
      }
      
      const routing: ChannelRouting = {
        assignments,
        total_physical_channels: totalChannels
      }
      
      await applyChannelRouting(routing)
      await validateConfig()
    }
  }, { immediate: true })

  // ── Retorno del store ─────────────────────────────────────────────────────
  return {
    // Dispositivos
    inputDevices,
    outputDevices,
    // Config activa
    selectedInputDevice,
    selectedOutputDevice,
    selectedSampleRate,
    selectedBufferSize,
    channelRouting,
    // Validación (#48)
    validationError,
    supportedSampleRates,
    supportedBufferSizes,
    // Estado del stream
    streamState,
    streamError,
    isLoading,
    // Compat
    isStreaming,
    /** @deprecated Usar selectedInputDevice */
    selectedInput: computed({
      get: () => selectedInputDevice.value?.id ?? '',
      set: (id: string) => {
        const dev = inputDevices.value.find(d => d.id === id)
        if (dev) {
          selectedInputDevice.value = dev
          _persistConfig()
        }
      }
    }),
    selectedOutput: computed({
      get: () => selectedOutputDevice.value?.id ?? '',
      set: (id: string) => {
        const dev = outputDevices.value.find(d => d.id === id)
        if (dev) {
          selectedOutputDevice.value = dev
          lsSet('audio.outputDeviceId', id)
        }
      }
    }),
    /** @deprecated Usar selectedSampleRate */
    sampleRate: selectedSampleRate,
    /** @deprecated Usar selectedBufferSize */
    bufferSize: selectedBufferSize,
    // Métricas
    currentLevel_dBFS,
    levelX_dBFS,
    levelY_dBFS,
    fftResult,
    estimatedLatencyMs,
    latencyEstimateMs,
    // Acciones
    loadDevices,
    startStream,
    stopStream,
    applyConfig,
    applyChannelRouting,
    loadSupportedSampleRates,
    validateConfig,
    listenToStreamEvents,
    cleanup,
    // Compat (síncrono → async)
    startStreamSync,
    stopStreamSync,
    // RTA config
    fftSize,
    windowType,
    avgMode,
    // RTA legacy (fftSize, windowType, avgMode los mantiene RTAView localmente)
  }
})
