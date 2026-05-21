import type { FFTOutput, FrequencyResponseOutput, FilterOutput } from '../types/dsp'

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
  fft:               (samples: number[], fs: number) => post<FFTOutput>('/analysis/fft', { samples, fs }),
  frequencyResponse: (x: number[], y: number[], fs: number) => post<FrequencyResponseOutput>('/analysis/frequency-response', { x, y, fs }),
  movingAverage:     (samples: number[], M: number, passes = 1) => post<FilterOutput>('/filters/moving-average', { samples, M, passes }),
}
