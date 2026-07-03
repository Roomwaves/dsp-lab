import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '../services/api'
import type { FrequencyResponseOutput } from '../types/dsp'

export type FilterType = 'moving-average' | 'comb' | 'fir'

export const useFilterStore = defineStore('filter', () => {
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const filterType = ref<FilterType>('moving-average')
  const fs = ref(44100)

  // Moving Average params
  const maM = ref(8)
  const maPasses = ref(1)

  // Comb filter params
  const combB0 = ref(1.0)
  const combB1 = ref(0.5)
  const combB2 = ref(0.25)

  // FIR params
  const firCoefficients = ref<number[]>([1, 0.5, 0.25, 0.125])
  const firText = ref<string>('1, 0.5, 0.25, 0.125')

  // Frequency response result
  const frequencies = ref<number[]>([])
  const magnitudeDb = ref<number[]>([])
  const phaseRad = ref<number[]>([])

  // Impulse response result
  const impulseSamples = ref<number[]>([])

  function parseFirText(text: string) {
    firText.value = text
    const coeffs = text
      .trim()
      .split(/[\s,;]+/)
      .map(Number)
      .filter(v => !isNaN(v))
    firCoefficients.value = coeffs
  }

  async function truncateFir(n: number) {
    if (firCoefficients.value.length === 0 || n <= 0 || n >= firCoefficients.value.length) return
    try {
      const res = await api.truncateFir(firCoefficients.value, n)
      firCoefficients.value = res.samples
      firText.value = res.samples.join(', ')
      await computeResponse()
    } catch (e) {
      error.value = (e as Error).message
    }
  }

  async function computeResponse(overrideFs?: number) {
    const activeFs = overrideFs ?? fs.value
    isLoading.value = true
    error.value = null
    try {
      let result: FrequencyResponseOutput
      let filterParamPayload: Record<string, unknown> = {}

      if (filterType.value === 'moving-average') {
        filterParamPayload = { M: maM.value, passes: maPasses.value }
        result = await api.filterResponse('moving-average', {
          ...filterParamPayload,
          fs: activeFs,
        })
      } else if (filterType.value === 'comb') {
        filterParamPayload = { b0: combB0.value, b1: combB1.value, b2: combB2.value }
        result = await api.filterResponse('comb', {
          ...filterParamPayload,
          fs: activeFs,
        })
      } else {
        filterParamPayload = { coefficients: firCoefficients.value }
        result = await api.filterResponse('fir', {
          ...filterParamPayload,
          fs: activeFs,
        })
      }

      frequencies.value = result.frequencies
      magnitudeDb.value = result.magnitude_db
      phaseRad.value = result.phase_rad

      // Compute impulse response h[n]
      const impRes = await api.impulseResponse(
        filterType.value === 'moving-average' ? 'moving_average' : filterType.value,
        filterParamPayload,
        128
      )
      impulseSamples.value = impRes.samples
    } catch (e) {
      error.value = (e as Error).message
    } finally {
      isLoading.value = false
    }
  }

  return {
    isLoading,
    error,
    filterType,
    fs,
    maM,
    maPasses,
    combB0,
    combB1,
    combB2,
    firCoefficients,
    firText,
    frequencies,
    magnitudeDb,
    phaseRad,
    impulseSamples,
    parseFirText,
    truncateFir,
    computeResponse,
  }
})
