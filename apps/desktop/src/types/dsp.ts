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
