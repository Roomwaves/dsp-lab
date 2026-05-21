import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAudioStore = defineStore('audio', () => {
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  
  // TODO: Add audio logic

  return { isLoading, error }
})
