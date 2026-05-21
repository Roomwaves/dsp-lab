import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useSignalStore } from './useSignalStore'
import { api } from '../services/api'

export interface AudioDevice {
  id: string;
  name: string;
}

export type FftSize = 1024 | 2048 | 4096
export type WindowType = 'hann' | 'hamming' | 'blackman' | 'rectangular'
export type AvgMode = 'off' | 8 | 16

export const useAudioStore = defineStore('audio', () => {
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const inputDevices = ref<AudioDevice[]>([
    { id: 'default', name: 'Default Input' },
    { id: 'mic1', name: 'Microphone (External)' }
  ])
  const outputDevices = ref<AudioDevice[]>([
    { id: 'default', name: 'Default Output' },
    { id: 'spk1', name: 'Speakers' }
  ])

  const selectedInput = ref('default')
  const selectedOutput = ref('default')

  const sampleRate = ref(44100)
  const bufferSize = ref(1024)

  const latencyEstimateMs = computed(() => {
    return (bufferSize.value / sampleRate.value) * 1000
  })

  // RTA stream state
  const isStreaming = ref(false)
  const fftSize = ref<FftSize>(4096)
  const windowType = ref<WindowType>('hann')
  const avgMode = ref<AvgMode>('off')

  let _animFrameId: number | null = null
  let _avgBuffer: number[][] = []

  async function _fetchAndUpdate() {
    if (!isStreaming.value) return
    const signalStore = useSignalStore()
    try {
      // Genera una muestra sintética via API para simular stream (en producción
      // esto vendrá de cpal/Tauri). Usamos las muestras existentes si hay.
      const n = fftSize.value
      if (signalStore.samples.length >= n) {
        const block = signalStore.samples.slice(-n)
        const result = await api.fft(block, sampleRate.value)
        let mags: number[] = result.magnitude

        // Aplicar promediado
        if (avgMode.value !== 'off') {
          const avgN = avgMode.value as number
          _avgBuffer.push(mags)
          if (_avgBuffer.length > avgN) _avgBuffer.shift()
          mags = _avgBuffer[0].map((_, i) =>
            _avgBuffer.reduce((sum, frame) => sum + frame[i], 0) / _avgBuffer.length
          )
        }

        signalStore.frequencies = result.frequencies
        signalStore.fftMagnitudes = mags
      }
    } catch {
      // Sin error visible en stream continuo
    }
    _animFrameId = requestAnimationFrame(() => {
      setTimeout(_fetchAndUpdate, 33) // ~30 fps
    })
  }

  function startStream() {
    if (isStreaming.value) return
    isStreaming.value = true
    _avgBuffer = []
    _fetchAndUpdate()
  }

  function stopStream() {
    isStreaming.value = false
    if (_animFrameId !== null) {
      cancelAnimationFrame(_animFrameId)
      _animFrameId = null
    }
  }

  return {
    isLoading, error,
    inputDevices, outputDevices,
    selectedInput, selectedOutput,
    sampleRate, bufferSize,
    latencyEstimateMs,
    // RTA
    isStreaming,
    fftSize,
    windowType,
    avgMode,
    startStream,
    stopStream,
  }
})
