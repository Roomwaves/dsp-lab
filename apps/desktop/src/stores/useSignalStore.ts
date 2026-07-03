import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { api } from '../services/api';

export interface ToneEntry {
  frequency: number;
  amplitude: number;
}

export const useSignalStore = defineStore('signal', () => {
  const signalType = ref<'sine' | 'square' | 'triangle' | 'white-noise' | 'pink-noise' | 'sweep'>('sine');

  // Pure tones (multi-tone sine)
  const tones = ref<ToneEntry[]>([
    { frequency: 440, amplitude: 1.0 },
  ]);

  // Single wave / noise parameters
  const frequency = ref(440);
  const amplitude = ref(0.8);
  const duty = ref(0.5);
  const width = ref(0.5);

  // Sweep parameters
  const fStart = ref(20);
  const fEnd = ref(20000);
  const sweepType = ref<'linear' | 'logarithmic'>('linear');

  // Global settings
  const fs = ref(44100);
  const duration = ref(1.0);
  const snrDb = ref(20);
  const applyNoise = ref(false);

  // Output data
  const samples = ref<number[]>([]);
  const fftFrequencies = ref<number[]>([]);
  const fftMagnitudes = ref<number[]>([]);
  const isLoading = ref(false);
  const isPlaying = ref(false);
  const error = ref<string | null>(null);

  const hasSamples = computed(() => samples.value.length > 0);

  let activeAudioCtx: AudioContext | null = null;
  let activeSourceNode: AudioBufferSourceNode | null = null;

  function addTone() {
    tones.value.push({ frequency: 1000, amplitude: 0.5 });
  }

  function removeTone(i: number) {
    if (tones.value.length > 1) tones.value.splice(i, 1);
  }

  async function generate() {
    isLoading.value = true;
    error.value = null;
    try {
      const params: any = {
        signalType: signalType.value,
        fs: fs.value,
        duration: duration.value,
        amplitude: amplitude.value,
        applyNoise: applyNoise.value,
        snrDb: snrDb.value,
      };

      if (signalType.value === 'sine') {
        params.frequencies = tones.value.map(t => t.frequency);
        params.amplitudes = tones.value.map(t => t.amplitude);
      } else if (signalType.value === 'square') {
        params.frequency = frequency.value;
        params.amplitude = amplitude.value;
        params.duty = duty.value;
      } else if (signalType.value === 'triangle') {
        params.frequency = frequency.value;
        params.amplitude = amplitude.value;
        params.width = width.value;
      } else if (signalType.value === 'white-noise' || signalType.value === 'pink-noise') {
        params.amplitude = amplitude.value;
      } else if (signalType.value === 'sweep') {
        params.fStart = fStart.value;
        params.fEnd = fEnd.value;
        params.sweepType = sweepType.value;
        params.amplitude = amplitude.value;
      }

      const result = await api.generateSignal(params);
      samples.value = result.samples;

      // Compute FFT spectrum for visualization
      const fftResult = await api.fft(samples.value, fs.value);
      fftFrequencies.value = fftResult.frequencies;
      fftMagnitudes.value = fftResult.magnitudes;
    } catch (e) {
      error.value = (e as Error).message;
    } finally {
      isLoading.value = false;
    }
  }

  async function exportWav() {
    if (!hasSamples.value) return;
    try {
      await api.downloadAudio(samples.value, fs.value);
    } catch (e) {
      error.value = (e as Error).message;
    }
  }

  function stopAudio() {
    if (activeSourceNode) {
      try {
        activeSourceNode.stop();
        activeSourceNode.disconnect();
      } catch {}
      activeSourceNode = null;
    }
    if (activeAudioCtx) {
      try {
        activeAudioCtx.close();
      } catch {}
      activeAudioCtx = null;
    }
    isPlaying.value = false;
  }

  function playAudio() {
    if (!hasSamples.value) return;
    stopAudio();

    try {
      const AudioCtxClass = window.AudioContext || (window as any).webkitAudioContext;
      activeAudioCtx = new AudioCtxClass({ sampleRate: fs.value });
      
      const audioBuffer = activeAudioCtx.createBuffer(1, samples.value.length, fs.value);
      const channelData = audioBuffer.getChannelData(0);
      for (let i = 0; i < samples.value.length; i++) {
        channelData[i] = samples.value[i];
      }

      activeSourceNode = activeAudioCtx.createBufferSource();
      activeSourceNode.buffer = audioBuffer;
      activeSourceNode.connect(activeAudioCtx.destination);
      
      activeSourceNode.onended = () => {
        isPlaying.value = false;
      };

      activeSourceNode.start();
      isPlaying.value = true;
    } catch (e) {
      error.value = `Error reproduciendo audio: ${(e as Error).message}`;
      isPlaying.value = false;
    }
  }

  return {
    signalType,
    tones,
    frequency,
    amplitude,
    duty,
    width,
    fStart,
    fEnd,
    sweepType,
    fs,
    duration,
    snrDb,
    applyNoise,
    samples,
    fftFrequencies,
    fftMagnitudes,
    isLoading,
    isPlaying,
    error,
    hasSamples,
    addTone,
    removeTone,
    generate,
    exportWav,
    playAudio,
    stopAudio,
  };
});
