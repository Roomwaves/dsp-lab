export interface ActiveSignal {
  filename: string;
  path: string;
  fs: number;
  duration: number;        // en segundos
  samples: number[];
}

export interface AnalysisParams {
  windowSize: 1024 | 2048 | 4096 | 8192;
  overlap: number;         // 0.0 a 0.95
  windowType: 'hann' | 'hamming' | 'blackman' | 'rectangular';
}

export const DEFAULT_ANALYSIS_PARAMS: AnalysisParams = {
  windowSize: 4096,
  overlap: 0.75,
  windowType: 'hann',
};

export interface ComputedResult {
  frequencies: number[];
  magnitude_db: number[];
  phase_rad: number[];
  coherence: number[];
  spectrum_x: number[];
  spectrum_y: number[];
}

export interface SnapshotParams {
  windowSize: number;
  overlap: number;
  windowType: string;
  sourceFiles: { x: string; y: string };
}

export interface Snapshot {
  id: string;
  label: string;
  color: string;
  visible: boolean;
  createdAt: number;
  params: SnapshotParams;
  data: ComputedResult;
}

export interface Session {
  x: ActiveSignal | null;
  y: ActiveSignal | null;
  params: AnalysisParams;
  snapshots: Snapshot[];
  liveResult: ComputedResult | null;
  isComputing: boolean;
  computeError: string | null;
}

// Exportar esta constante para usarla en el store
export const SNAPSHOT_COLORS = [
  '#00D97E',   // accent verde (default primero)
  '#3B82F6',   // azul
  '#F59E0B',   // amarillo
  '#EF4444',   // rojo
  '#8B5CF6',   // violeta
  '#EC4899',   // rosa
  '#14B8A6',   // teal
  '#F97316',   // naranja
] as const;
