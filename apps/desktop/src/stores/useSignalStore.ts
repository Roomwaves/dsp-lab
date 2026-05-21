import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useSignalStore = defineStore('signal', () => {
  const samples = ref<number[]>([])
  const fs = ref<number>(44100)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

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

  const durationSeconds = computed(() => samples.value.length / fs.value)

  return { samples, fs, isLoading, error, durationSeconds, loadFromFile }
})
