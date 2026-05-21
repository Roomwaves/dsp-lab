import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface AudioDevice {
  id: string;
  name: string;
}

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

  return { 
    isLoading, error, 
    inputDevices, outputDevices, 
    selectedInput, selectedOutput, 
    sampleRate, bufferSize,
    latencyEstimateMs
  }
})
