import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useCoherenceStore = defineStore('coherence', () => {
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  
  // TODO: Add coherence logic

  return { isLoading, error }
})
