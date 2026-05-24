// Tipos de audio sincronizados con las estructuras Rust del backend Tauri.
// Reflejan AudioDeviceInfo, SupportedConfig, ChannelRouting, etc.

/** Rango de configuración soportado por un dispositivo de audio. */
export interface SupportedConfig {
  channels: number
  min_sample_rate: number
  max_sample_rate: number
  sample_format: 'f32' | 'i16' | 'i32' | 'u8' | string
  buffer_size_range: [number, number] | null
}

/** Información completa de un dispositivo de audio del sistema. */
export interface AudioDeviceInfo {
  /** ID estable (hash del nombre del dispositivo). */
  id: string
  /** Nombre legible por humanos. */
  name: string
  /** "input" | "output" | "duplex" */
  device_type: string
  is_default: boolean
  supported_configs: SupportedConfig[]
}

/** Configuración para abrir un stream de audio. */
export interface AudioStreamConfig {
  device_id: string
  sample_rate: number
  channels: number
  buffer_size: number
}

/** Asignación entre un canal lógico y un canal físico del dispositivo. */
export interface ChannelAssignment {
  /** Nombre lógico: "X (input)", "Y (output)", "Reference", etc. */
  logical_name: string
  /** Índice 0-based del canal físico en el stream. */
  physical_channel: number
}

/** Configuración completa de routing de canales. */
export interface ChannelRouting {
  assignments: ChannelAssignment[]
  total_physical_channels: number
}

/** Resultado de FFT emitido por el evento `audio://fft-result`. */
export interface FFTResult {
  frequencies: number[]
  magnitudes_db: number[]
  level_dbfs: number
  channel_levels_dbfs: number[]
  timestamp_ms: number
}

/** Estados posibles del stream de audio. */
export type StreamState = 'stopped' | 'starting' | 'running' | 'error'
