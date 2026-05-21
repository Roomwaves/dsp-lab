import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { v4 as uuidv4 } from 'uuid';
import type { Snapshot, ComputedResult, AnalysisParams, ActiveSignal } from '../types';
import { DEFAULT_ANALYSIS_PARAMS, SNAPSHOT_COLORS } from '../types';
import { api } from '../services/api';

export const useMeasurementSession = defineStore('measurementSession', () => {

  // ─── State ───────────────────────────────────────────────────────────────

  const x = ref<ActiveSignal | null>(null);
  const y = ref<ActiveSignal | null>(null);
  const params = ref<AnalysisParams>({ ...DEFAULT_ANALYSIS_PARAMS });
  const snapshots = ref<Snapshot[]>([]);
  const liveResult = ref<ComputedResult | null>(null);
  const isComputing = ref(false);
  const computeError = ref<string | null>(null);

  // ─── Getters ─────────────────────────────────────────────────────────────

  const hasSignals = computed(() => x.value !== null && y.value !== null);
  const hasLiveResult = computed(() => liveResult.value !== null);
  const visibleSnapshots = computed(() => snapshots.value.filter(s => s.visible));

  const nextSnapshotColor = computed(() => {
    const usedColors = new Set(snapshots.value.map(s => s.color));
    return SNAPSHOT_COLORS.find(c => !usedColors.has(c)) ?? SNAPSHOT_COLORS[0];
  });

  const nextSnapshotLabel = computed(() =>
    `Medición ${snapshots.value.length + 1}`
  );

  // ─── Actions ─────────────────────────────────────────────────────────────

  /**
   * Carga una señal en el slot X o Y.
   * Acepta un File (drag & drop o file picker).
   * Sube el archivo a la API y recibe samples + metadata.
   * Si ambos slots están llenos después de cargar, dispara compute().
   */
  async function loadSignal(slot: 'x' | 'y', file: File): Promise<void> {
    try {
      const res = await api.uploadAudio(file);
      const signal: ActiveSignal = {
        filename: file.name,
        path: '', // The backend doesn't return the path, we can leave it empty
        fs: res.fs,
        duration: res.duration_s,
        samples: res.samples,
      };

      if (slot === 'x') {
        x.value = signal;
      } else {
        y.value = signal;
      }

      if (hasSignals.value) {
        if (x.value!.fs !== y.value!.fs) {
          computeError.value = `Sample rate mismatch: X is ${x.value!.fs}Hz, Y is ${y.value!.fs}Hz`;
          return;
        }
        await compute();
      }
    } catch (e) {
      computeError.value = `Failed to load signal: ${(e as Error).message}`;
    }
  }

  /**
   * Computa todos los resultados a partir de los signals actuales y params.
   * Llama a la API en paralelo para todos los endpoints necesarios.
   * Actualiza liveResult con el resultado consolidado.
   */
  async function compute(): Promise<void> {
    if (!hasSignals.value) return;
    if (x.value!.fs !== y.value!.fs) {
      computeError.value = `Sample rate mismatch: X is ${x.value!.fs}Hz, Y is ${y.value!.fs}Hz`;
      return;
    }

    isComputing.value = true;
    computeError.value = null;

    try {
      const fs = x.value!.fs;
      const xSamples = x.value!.samples;
      const ySamples = y.value!.samples;

      const [freqResp, coher, fftX, fftY] = await Promise.all([
        api.frequencyResponse(xSamples, ySamples, fs),
        api.coherence(xSamples, ySamples, fs), // api takes (x, y, fs, averages?)
        api.fft(xSamples, fs),
        api.fft(ySamples, fs),
      ]);

      liveResult.value = {
        frequencies: freqResp.frequencies,
        magnitude_db: freqResp.magnitude_db,
        phase_rad: freqResp.phase_rad,
        coherence: coher.coherence,
        spectrum_x: fftX.magnitudes,
        spectrum_y: fftY.magnitudes,
      };
    } catch (e) {
      computeError.value = (e as Error).message;
    } finally {
      isComputing.value = false;
    }
  }

  /**
   * Recalcula con nuevos parámetros de análisis.
   * Actualiza params y llama compute().
   */
  async function updateParams(newParams: Partial<AnalysisParams>): Promise<void> {
    params.value = { ...params.value, ...newParams };
    if (hasSignals.value) await compute();
  }

  /**
   * Guarda el liveResult actual como un snapshot.
   * Solo funciona si hay un liveResult disponible.
   */
  function captureSnapshot(): Snapshot | null {
    if (!liveResult.value || !x.value || !y.value) return null;

    const snapshot: Snapshot = {
      id: uuidv4(),
      label: nextSnapshotLabel.value,
      color: nextSnapshotColor.value,
      visible: true,
      createdAt: Date.now(),
      params: {
        windowSize: params.value.windowSize,
        overlap: params.value.overlap,
        windowType: params.value.windowType,
        sourceFiles: { x: x.value.filename, y: y.value.filename },
      },
      data: { ...liveResult.value },
    };

    snapshots.value.push(snapshot);
    return snapshot;
  }

  /**
   * Elimina un snapshot por id.
   */
  function removeSnapshot(id: string): void {
    snapshots.value = snapshots.value.filter(s => s.id !== id);
  }

  /**
   * Cambia la visibilidad de un snapshot en los gráficos.
   */
  function toggleSnapshot(id: string): void {
    const s = snapshots.value.find(s => s.id === id);
    if (s) s.visible = !s.visible;
  }

  /**
   * Renombra un snapshot.
   */
  function renameSnapshot(id: string, label: string): void {
    const s = snapshots.value.find(s => s.id === id);
    if (s) s.label = label;
  }

  /**
   * Limpia toda la sesión.
   */
  function resetSession(): void {
    x.value = null;
    y.value = null;
    snapshots.value = [];
    liveResult.value = null;
    computeError.value = null;
    isComputing.value = false;
  }

  return {
    // State
    x, y, params, snapshots, liveResult, isComputing, computeError,
    // Getters
    hasSignals, hasLiveResult, visibleSnapshots, nextSnapshotColor, nextSnapshotLabel,
    // Actions
    loadSignal, compute, updateParams, captureSnapshot,
    removeSnapshot, toggleSnapshot, renameSnapshot, resetSession,
  };
});
