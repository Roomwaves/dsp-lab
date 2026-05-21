import type { FFTOutput, FrequencyResponseOutput, FilterOutput, CoherenceOutput, GeneratedSignalOutput } from '../types/dsp'

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) {
    const detail = await res.json().catch(() => ({}))
    throw new Error(detail?.detail ?? `API error ${res.status}`)
  }
  return res.json()
}


export const api = {
  fft: (samples: number[], fs: number) =>
    post<FFTOutput>('/analysis/fft', { samples, fs }),

  frequencyResponse: (x: number[], y: number[], fs: number) =>
    post<FrequencyResponseOutput>('/analysis/frequency-response', { x, y, fs }),

  coherence: (x: number[], y: number[], fs: number, averages = 8) =>
    post<CoherenceOutput>('/analysis/coherence', { x, y, fs, averages }),

  movingAverage: (samples: number[], M: number, passes = 1) =>
    post<FilterOutput>('/filters/moving-average', { samples, M, passes }),

  filterResponse: (type: 'moving-average' | 'comb' | 'fir', params: Record<string, unknown>) =>
    post<FrequencyResponseOutput>(`/filters/${type}/response`, params),

  generatePureTones: (frequencies: number[], amplitudes: number[], fs: number, duration: number) =>
    post<GeneratedSignalOutput>('/signals/pure-tones', { frequencies, amplitudes, fs, duration }),

  addWhiteNoise: (samples: number[], fs: number, snrDb: number) =>
    post<GeneratedSignalOutput>('/signals/add-noise', { samples, fs, snr_db: snrDb }),

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
