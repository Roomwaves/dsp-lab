export interface FFTOutput {
  frequencies: number[]
  magnitude: number[]
  phase: number[]
}

export interface FrequencyResponseOutput {
  frequencies: number[]
  magnitude: number[]
  phase: number[]
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
