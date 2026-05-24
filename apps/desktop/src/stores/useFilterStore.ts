import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '../services/api'
import type { FrequencyResponseOutput } from '../types/dsp'

export type FilterType = 'moving-average' | 'comb' | 'fir'

export const useFilterStore = defineStore('filter', () => {
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const filterType = ref<FilterType>('moving-average')

  // Moving Average params
  const maM = ref(8)
  const maPasses = ref(1)

  // Comb filter params
  const combB0 = ref(1.0)
  const combB1 = ref(0.5)
  const combB2 = ref(0.25)

  // FIR params
  const firCoefficients = ref<number[]>([])

  // Frequency response result
  const frequencies = ref<number[]>([])
  const magnitudeDb = ref<number[]>([])
  const phaseRad = ref<number[]>([])

  async function computeResponse(fs = 44100) {
    isLoading.value = true
    error.value = null
    try {
      let result: FrequencyResponseOutput
      if (filterType.value === 'moving-average') {
        result = await api.filterResponse('moving-average', {
          M: maM.value,
          passes: maPasses.value,
          fs,
        })
      } else if (filterType.value === 'comb') {
        result = await api.filterResponse('comb', {
          b0: combB0.value,
          b1: combB1.value,
          b2: combB2.value,
          fs,
        })
      } else {
        result = await api.filterResponse('fir', {
          coefficients: firCoefficients.value,
          fs,
        })
      }
      frequencies.value = result.frequencies
      magnitudeDb.value = result.magnitude_db
      phaseRad.value = result.phase_rad
    } catch (e) {
      error.value = (e as Error).message
    } finally {
      isLoading.value = false
    }
  }

  return {
    isLoading, error,
    filterType,
    maM, maPasses,
    combB0, combB1, combB2,
    firCoefficients,
    frequencies, magnitudeDb, phaseRad,
    computeResponse,
  }
})
