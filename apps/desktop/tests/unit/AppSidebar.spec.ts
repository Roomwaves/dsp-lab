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

const mockAppStore = {
  toggleSettings: vi.fn(),
  appMode: 'file',
  setAppMode: vi.fn()
};

vi.mock('../../src/stores/useAppStore', () => ({
  useAppStore: () => mockAppStore
}));

describe('AppSidebar.vue', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    vi.clearAllMocks();
    mockAppStore.appMode = 'file';
  });

  it('debería renderizar el botón de cambiar de modo y de configuración', () => {
    const wrapper = mount(AppSidebar);
    expect(wrapper.text()).toContain('Cambiar de Modo');
    expect(wrapper.text()).toContain('sidebar.settings');
  });

  it('debería renderizar la etiqueta del modo actual', () => {
    const wrapper = mount(AppSidebar);
    expect(wrapper.find('.mode-badge').text()).toBe('Archivos');
  });

  it('debería renderizar el panel de parámetros si hay señales cargadas', async () => {
    const session = useMeasurementSession();
    // Forzar que tenga señales
    session.x = { filename: 'x.wav', path: '', fs: 44100, duration: 1, samples: [0] };
    session.y = { filename: 'y.wav', path: '', fs: 44100, duration: 1, samples: [0] };
    
    const wrapper = mount(AppSidebar);
    expect(wrapper.text()).toContain('PARÁMETROS');
    expect(wrapper.find('#fft-size-select').exists()).toBe(true);
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
