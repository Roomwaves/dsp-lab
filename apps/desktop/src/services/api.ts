import type { FFTOutput, FrequencyResponseOutput, FilterOutput, CoherenceOutput, GeneratedSignalOutput } from '../types/dsp'
import type { AnalysisParams } from '../types/session'

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

async function post<T>(path: string, body: unknown): Promise<T> {
  let res: Response
  try {
    res = await fetch(`${API_BASE}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
  } catch (err) {
    throw new Error(
      "No se pudo conectar con el servidor API. Asegurate de que el backend esté corriendo (por ejemplo, con 'npm run docker:up' o 'npm run api:dev')."
    )
  }

  if (!res.ok) {
    const detail = await res.json().catch(() => ({}))
    throw new Error(detail?.detail ?? `API error ${res.status}`)
  }
  return res.json()
}


export const api = {
  uploadAudio: async (file: File): Promise<{
    samples: number[]
    fs: number
    duration_s: number
    channels: number
  }> => {
    const formData = new FormData()
    formData.append('file', file)
    let res: Response
    try {
      res = await fetch(`${API_BASE}/io/upload`, {
        method: 'POST',
        body: formData,
      })
    } catch (err) {
      throw new Error(
        "No se pudo conectar con el servidor API. Asegurate de que el backend esté corriendo (por ejemplo, con 'npm run docker:up' o 'npm run api:dev')."
      )
    }

    if (!res.ok) {
      const detail = await res.json().catch(() => ({}))
      throw new Error(detail?.detail ?? `API error ${res.status}`)
    }
    return res.json()
  },

  fft: (samples: number[], fs: number, params?: AnalysisParams) =>
    post<FFTOutput>('/analysis/fft', { samples, fs, ...params }),

  frequencyResponse: (x: number[], y: number[], fs: number, params?: AnalysisParams) =>
    post<FrequencyResponseOutput>('/analysis/frequency-response', { x, y, fs, ...params }),

  coherence: (x: number[], y: number[], fs: number, paramsOrAverages?: AnalysisParams | number) => {
    const payload: any = { x, y, fs }
    if (typeof paramsOrAverages === 'number') {
      payload.averages = paramsOrAverages
    } else if (paramsOrAverages) {
      Object.assign(payload, paramsOrAverages)
    }
    return post<CoherenceOutput>('/coherence/compute', payload)
  },

  movingAverage: (samples: number[], M: number, passes = 1) =>
    post<FilterOutput>('/filters/moving-average', { samples, M, passes }),

  filterResponse: (type: 'moving-average' | 'comb' | 'fir', params: Record<string, unknown>) =>
    post<FrequencyResponseOutput>(`/filters/${type}/response`, params),

  generatePureTones: (frequencies: number[], amplitudes: number[], fs: number, duration: number) =>
    post<GeneratedSignalOutput>('/signals/pure-tones', { frequencies, amplitudes, fs, duration }),

  addWhiteNoise: (samples: number[], fs: number, snrDb: number) =>
    post<GeneratedSignalOutput>('/signals/add-noise', { samples, fs, snr_db: snrDb }),

  generateSignal: (params: {
    signalType: string
    fs: number
    duration: number
    amplitude: number
    frequencies?: number[]
    amplitudes?: number[]
    frequency?: number
    fStart?: number
    fEnd?: number
    sweepType?: string
    applyNoise?: boolean
    snrDb?: number
  }) => post<GeneratedSignalOutput>('/signals/generate', params),


  downloadAudio: async (samples: number[], fs: number): Promise<void> => {
    const res = await fetch(`${API_BASE}/signals/export-wav`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ samples, fs }),
    })
    if (!res.ok) throw new Error(`API error ${res.status}`)
    const blob = await res.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'signal.wav'
    a.click()
    URL.revokeObjectURL(url)
  },
}
