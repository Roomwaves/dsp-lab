import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '../services/api'

export const useSignalStore = defineStore('signal', () => {
  const samples = ref<number[]>([])
  const fs = ref<number>(44100)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // FFT result (actualizado por el stream o por análisis batch)
  const frequencies = ref<number[]>([])
  const fftMagnitudes = ref<number[]>([])
  const fftResult = computed(() => ({
    frequencies: frequencies.value,
    magnitudes: fftMagnitudes.value,
  }))

  async function loadFromFile(file: File) {
    isLoading.value = true
    error.value = null
    try {
      // TODO: implementation
      console.log('Loading file', file.name)
    } catch (e) {
      error.value = (e as Error).message
    } finally {
      isLoading.value = false
    }
  }

  async function runFFT(fftSize = 4096) {
    if (samples.value.length === 0) return
    isLoading.value = true
    error.value = null
    try {
      const block = samples.value.slice(-fftSize)
      const result = await api.fft(block, fs.value)
      frequencies.value = result.frequencies
      fftMagnitudes.value = result.magnitude
    } catch (e) {
      error.value = (e as Error).message
    } finally {
      isLoading.value = false
    }
  }

  const durationSeconds = computed(() => samples.value.length / fs.value)

  return {
    samples, fs, isLoading, error,
    durationSeconds, loadFromFile,
    frequencies, fftMagnitudes, fftResult,
    runFFT,
  }
})
