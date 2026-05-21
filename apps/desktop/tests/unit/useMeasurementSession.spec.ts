import { describe, it, expect, beforeEach, vi } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useMeasurementSession } from '../../src/stores/useMeasurementSession';
import { api } from '../../src/services/api';

vi.mock('../../src/services/api', () => ({
  api: {
    uploadAudio: vi.fn(),
    fft: vi.fn(),
    frequencyResponse: vi.fn(),
    coherence: vi.fn(),
  }
}));

describe('useMeasurementSession Pinia Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    vi.clearAllMocks();
  });

  it('debería validar tamaño menor a 100MB y formato .wav al cargar', async () => {
    const session = useMeasurementSession();
    
    // Test tamaño > 100MB
    const bigFile = new File(['a'.repeat(101 * 1024 * 1024)], 'test.wav', { type: 'audio/wav' });
    await session.loadSignal('x', bigFile);
    expect(session.computeError).toContain('100MB');
    expect(session.x).toBeNull();

    // Test formato no .wav
    const badFile = new File(['samples'], 'test.mp3', { type: 'audio/mp3' });
    await session.loadSignal('x', badFile);
    expect(session.computeError).toContain('archivo .wav');
    expect(session.x).toBeNull();
  });

  it('debería disparar compute() si ambos slots están llenos con fs compatible', async () => {
    const mockUpload = vi.mocked(api.uploadAudio);
    mockUpload.mockResolvedValue({
      samples: [0.1, 0.2, 0.3],
      fs: 44100,
      duration_s: 1.0,
      channels: 1
    });

    const mockFreqResponse = vi.mocked(api.frequencyResponse).mockResolvedValue({
      frequencies: [100, 200],
      magnitude_db: [-3, -6],
      phase_rad: [0, 0]
    });
    const mockCoherence = vi.mocked(api.coherence).mockResolvedValue({
      frequencies: [100, 200],
      coherence: [0.99, 0.98]
    });
    const mockFFT = vi.mocked(api.fft).mockResolvedValue({
      frequencies: [100, 200],
      magnitudes: [0.5, 0.6]
    });

    const session = useMeasurementSession();
    const fileX = new File(['a'], 'x.wav', { type: 'audio/wav' });
    const fileY = new File(['b'], 'y.wav', { type: 'audio/wav' });

    // Carga X
    await session.loadSignal('x', fileX);
    expect(session.x).not.toBeNull();
    expect(mockFreqResponse).not.toHaveBeenCalled();

    // Carga Y (ambas cargadas)
    await session.loadSignal('y', fileY);
    expect(session.y).not.toBeNull();

    // Verifica que compute() fue disparado
    expect(mockFreqResponse).toHaveBeenCalled();
    expect(mockCoherence).toHaveBeenCalled();
    expect(mockFFT).toHaveBeenCalledTimes(2);

    expect(session.liveResult).not.toBeNull();
    expect(session.liveResult?.coherence).toEqual([0.99, 0.98]);
  });

  it('debería fallar y no computar si las señales tienen distinto fs, mostrando ambos en el mensaje', async () => {
    const mockUpload = vi.mocked(api.uploadAudio);
    
    // Primero sube X a 44100Hz
    mockUpload.mockResolvedValueOnce({
      samples: [0.1, 0.2],
      fs: 44100,
      duration_s: 1.0,
      channels: 1
    });
    // Luego sube Y a 48000Hz
    mockUpload.mockResolvedValueOnce({
      samples: [0.3, 0.4],
      fs: 48000,
      duration_s: 1.0,
      channels: 1
    });

    const mockFreqResponse = vi.mocked(api.frequencyResponse);

    const session = useMeasurementSession();
    const fileX = new File(['a'], 'x.wav', { type: 'audio/wav' });
    const fileY = new File(['b'], 'y.wav', { type: 'audio/wav' });

    await session.loadSignal('x', fileX);
    await session.loadSignal('y', fileY);

    expect(session.y).not.toBeNull();
    expect(session.y?.fs).toBe(48000);
    expect(session.computeError).toContain('44100');
    expect(session.computeError).toContain('48000');
    expect(mockFreqResponse).not.toHaveBeenCalled();
    expect(session.liveResult).toBeNull();
  });

  it('debería limpiar liveResult en caso de reemplazar un slot con datos', async () => {
    const mockUpload = vi.mocked(api.uploadAudio).mockResolvedValue({
      samples: [0.1, 0.2],
      fs: 44100,
      duration_s: 1.0,
      channels: 1
    });
    vi.mocked(api.frequencyResponse).mockResolvedValue({
      frequencies: [100], magnitude_db: [-3], phase_rad: [0]
    });
    vi.mocked(api.coherence).mockResolvedValue({
      frequencies: [100], coherence: [0.99]
    });
    vi.mocked(api.fft).mockResolvedValue({
      frequencies: [100], magnitudes: [0.5]
    });

    const session = useMeasurementSession();
    
    await session.loadSignal('x', new File(['a'], 'x.wav'));
    await session.loadSignal('y', new File(['b'], 'y.wav'));
    expect(session.liveResult).not.toBeNull();

    // Reemplazar X limpia liveResult antes de recomputar
    const promise = session.loadSignal('x', new File(['c'], 'x2.wav'));
    expect(session.liveResult).toBeNull(); // Se limpia inmediatamente al cargar
    await promise;

    expect(session.liveResult).not.toBeNull(); // Vuelve a computar al terminar
  });

  it('debería realizar las 4 llamadas de API en paralelo y no limpiar liveResult anterior si falla una de ellas', async () => {
    const mockUpload = vi.mocked(api.uploadAudio).mockResolvedValue({
      samples: [0.1, 0.2],
      fs: 44100,
      duration_s: 1.0,
      channels: 1
    });
    
    // Primera computación exitosa
    vi.mocked(api.frequencyResponse).mockResolvedValueOnce({
      frequencies: [100], magnitude_db: [-3], phase_rad: [0]
    });
    vi.mocked(api.coherence).mockResolvedValueOnce({
      frequencies: [100], coherence: [0.99]
    });
    vi.mocked(api.fft).mockResolvedValue({
      frequencies: [100], magnitudes: [0.5]
    });

    const session = useMeasurementSession();
    await session.loadSignal('x', new File(['a'], 'x.wav'));
    await session.loadSignal('y', new File(['b'], 'y.wav'));
    expect(session.liveResult).not.toBeNull();
    const firstResult = session.liveResult;

    // Segunda computación falla en una de las llamadas (ej. coherence)
    vi.mocked(api.frequencyResponse).mockResolvedValueOnce({
      frequencies: [100], magnitude_db: [-3], phase_rad: [0]
    });
    vi.mocked(api.coherence).mockRejectedValueOnce(new Error('Coherence service down'));

    // Forzar re-cómputo cambiando parámetros
    await session.updateParams({ windowSize: 2048 });

    expect(session.computeError).toContain('Coherence service down');
    // liveResult NO se nullifica — mantiene el último resultado válido
    expect(session.liveResult).toBe(firstResult);
  });

  it('debería limitar la captura de snapshots a un máximo de 8', () => {
    const session = useMeasurementSession();
    session.x = { filename: 'x.wav', path: '', fs: 44100, duration: 1.0, samples: [0.1] };
    session.y = { filename: 'y.wav', path: '', fs: 44100, duration: 1.0, samples: [0.2] };
    session.liveResult = {
      frequencies: [100],
      magnitude_db: [-3],
      phase_rad: [0],
      coherence: [0.99],
      spectrum_x: [0.5],
      spectrum_y: [0.6]
    };

    // Agregar 8 snapshots
    for (let i = 0; i < 8; i++) {
      const snap = session.captureSnapshot();
      expect(snap).not.toBeNull();
    }
    expect(session.snapshots.length).toBe(8);

    // Intentar el noveno debe lanzar un error
    expect(() => session.captureSnapshot()).toThrow('Máximo 8 capturas');
    expect(session.snapshots.length).toBe(8);
  });
});
