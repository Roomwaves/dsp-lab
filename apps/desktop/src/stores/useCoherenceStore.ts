import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '../services/api'

export const useCoherenceStore = defineStore('coherence', () => {
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const frequencies = ref<number[]>([])
  const coherence = ref<number[]>([])

  // CH1 y CH2 samples
  const samplesX = ref<number[]>([])
  const samplesY = ref<number[]>([])
  const fs = ref(44100)
  const averages = ref(8)

  async function compute() {
    if (samplesX.value.length === 0 || samplesY.value.length === 0) return
    isLoading.value = true
    error.value = null
    try {
      const result = await api.coherence(samplesX.value, samplesY.value, fs.value, averages.value)
      frequencies.value = result.frequencies
      coherence.value = result.coherence
    } catch (e) {
      error.value = (e as Error).message
    } finally {
      isLoading.value = false
    }
  }

  return {
    isLoading, error,
    frequencies, coherence,
    samplesX, samplesY,
    fs, averages,
    compute,
  }
})
