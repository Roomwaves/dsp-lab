import { describe, it, expect, beforeEach, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import { setActivePinia, createPinia } from 'pinia';
import AppSidebar from '../../src/components/layout/AppSidebar.vue';
import { useMeasurementSession } from '../../src/stores/useMeasurementSession';

vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    t: (key: string) => key
  })
}));

vi.mock('../../src/stores/useAppStore', () => ({
  useAppStore: () => ({
    toggleSettings: vi.fn(),
  })
}));

vi.mock('../../src/services/api', () => ({
  api: {
    uploadAudio: vi.fn(),
    fft: vi.fn(),
    frequencyResponse: vi.fn(),
    coherence: vi.fn(),
  }
}));

describe('AppSidebar.vue', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    vi.clearAllMocks();
  });

  it('debería renderizar las dos drop zones para X e Y', () => {
    const wrapper = mount(AppSidebar);
    const dropZones = wrapper.findAll('.drop-zone');
    expect(dropZones.length).toBe(2);
    expect(dropZones[0].text()).toContain('X (Referencia)');
    expect(dropZones[1].text()).toContain('Y (Medición)');
  });

  it('debería mostrar error si el archivo es mayor a 100MB y no intentar cargarlo en el store', async () => {
    const wrapper = mount(AppSidebar);
    const session = useMeasurementSession();
    const loadSpy = vi.spyOn(session, 'loadSignal');

    // Simular el drop de un archivo > 100MB
    const bigFile = new File(['a'.repeat(101 * 1024 * 1024)], 'too_big.wav', { type: 'audio/wav' });
    const dropZone = wrapper.find('.drop-zone');
    
    // Obtener la instancia del componente para llamar directamente a handleFile
    const vm = wrapper.vm as any;
    await vm.handleFile('x', bigFile);

    expect(loadSpy).not.toHaveBeenCalled();
    expect(wrapper.text()).toContain('excede el tamaño máximo de 100MB');
  });

  it('debería mostrar error si el archivo no es .wav y no intentar cargarlo', async () => {
    const wrapper = mount(AppSidebar);
    const session = useMeasurementSession();
    const loadSpy = vi.spyOn(session, 'loadSignal');

    const badFile = new File(['samples'], 'test.mp3', { type: 'audio/mp3' });
    const vm = wrapper.vm as any;
    await vm.handleFile('x', badFile);

    expect(loadSpy).not.toHaveBeenCalled();
    expect(wrapper.text()).toContain('Solo archivos .wav');
  });

  it('debería renderizar la lista de capturas si existen snapshots', async () => {
    const session = useMeasurementSession();
    session.snapshots = [
      {
        id: '1',
        label: 'Captura A',
        color: '#ff0000',
        visible: true,
        createdAt: Date.now(),
        params: { windowSize: 4096, overlap: 0.75, windowType: 'hann', sourceFiles: { x: 'x.wav', y: 'y.wav' } },
        data: {} as any
      }
    ];

    const wrapper = mount(AppSidebar);
    const snapshotItems = wrapper.findAll('.snapshot-item');
    expect(snapshotItems.length).toBe(1);
    expect(snapshotItems[0].text()).toContain('Captura A');
  });
});
