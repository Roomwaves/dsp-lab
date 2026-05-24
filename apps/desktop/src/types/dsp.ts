export interface FFTOutput {
  frequencies: number[]
  magnitudes: number[]
}

export interface FrequencyResponseOutput {
  frequencies: number[]
  magnitude_db: number[]
  phase_rad: number[]
}

export interface FilterOutput {
  samples: number[]
  fs: number
}

export interface CoherenceOutput {
  frequencies: number[]
  coherence: number[]
}

export interface GeneratedSignalOutput {
  samples: number[]
  fs: number
  duration: number
}
