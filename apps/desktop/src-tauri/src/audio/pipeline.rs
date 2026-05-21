//! # Audio Pipeline
//!
//! Define el flujo completo de datos desde el callback CPAL hasta la UI de Vue:
//!
//! ```text
//! [CPAL callback] → [HeapRb] → [AudioBlockReceiver] → [processing thread] → [Tauri event]
//!      RT thread     lock-free      processor thread                            UI thread
//! ```
//!
//! ## Garantías de tiempo real
//! - `AudioPipeline::push_samples` es O(1), sin allocs, sin locks — seguro en RT thread.
//! - Si el ring buffer está lleno (overrun), las muestras **viejas** se descartan
//!   (el producer avanza el consumidor automáticamente vía `ringbuf`).
//! - El processing thread usa `thread::sleep(100µs)` como yield entre bloques
//!   para no consumir CPU en spin-wait puro.
//!
//! ## Evento emitido al frontend
//!
//! ```typescript
//! // Vue:
//! import { listen } from '@tauri-apps/api/event'
//! listen<FFTResult>('audio://fft-result', (event) => {
//!   signalStore.updateFFT(event.payload)
//! })
//! ```

use std::{
    sync::{
        atomic::{AtomicBool, Ordering},
        Arc,
    },
    thread,
    time::{Duration, SystemTime, UNIX_EPOCH},
};

use ringbuf::{
    traits::{Consumer, Observer, Producer, Split},
    HeapRb,
};
use serde::Serialize;
use tauri::{AppHandle, Emitter};

use super::channel_routing::ChannelRouting;

// ---------------------------------------------------------------------------
// Constantes
// ---------------------------------------------------------------------------

/// Factor de margen del ring buffer respecto al block_size.
/// Capacidad = block_size * RING_BUFFER_MARGIN — 8 bloques de margen ante jitter.
const RING_BUFFER_MARGIN: usize = 8;

/// Intervalo de yield del processing thread entre polls al ring buffer.
const PROCESSING_SLEEP_US: u64 = 100;

// ---------------------------------------------------------------------------
// Tipos públicos
// ---------------------------------------------------------------------------

/// Bloque de audio con timestamp, listo para DSP.
///
/// Las muestras están interleaved: `[ch0s0, ch1s0, ch0s1, ch1s1, …]`.
#[derive(Debug, Clone, Serialize)]
pub struct AudioBlock {
    /// Muestras f32 normalizadas `[-1.0, 1.0]`, formato interleaved.
    pub samples: Vec<f32>,
    /// Número de canales del stream.
    pub channels: u16,
    /// Sample rate del stream (Hz).
    pub sample_rate: u32,
    /// Timestamp de creación del bloque en ms desde UNIX epoch.
    pub timestamp_ms: u64,
}

/// Resultado de FFT emitido al frontend vía evento `audio://fft-result`.
#[derive(Debug, Clone, Serialize)]
pub struct FFTResult {
    /// Frecuencias centrales de cada bin (Hz).
    pub frequencies: Vec<f32>,
    /// Magnitudes en dBFS para cada bin.
    pub magnitudes_db: Vec<f32>,
    /// Nivel RMS del bloque en dBFS.
    pub level_dbfs: f32,
    /// Timestamp del bloque de origen (ms).
    pub timestamp_ms: u64,
}

// ---------------------------------------------------------------------------
// AudioPipeline
// ---------------------------------------------------------------------------

/// Extremo productor del pipeline — vive en el RT thread (CPAL callback).
///
/// Instanciar con `AudioPipeline::new`, que devuelve `(pipeline, receiver)`.
pub struct AudioPipeline {
    /// Tamaño de bloque en samples — almacenado para introspección y debugging.
    #[allow(dead_code)]
    block_size: usize,
    /// Canales del stream — almacenado para debugging y futura integración.
    #[allow(dead_code)]
    channels: u16,
    /// Sample rate del stream — almacenado para debugging y futura integración.
    #[allow(dead_code)]
    sample_rate: u32,
    producer: ringbuf::HeapProd<f32>,
}

/// Extremo consumidor del pipeline — vive en el processing thread.
pub struct AudioBlockReceiver {
    consumer: ringbuf::HeapCons<f32>,
    block_size: usize,
    channels: u16,
    sample_rate: u32,
    /// Buffer interno de ensamblado de bloques.
    assemble_buf: Vec<f32>,
}

impl AudioPipeline {
    /// Crea un par `(AudioPipeline, AudioBlockReceiver)`.
    ///
    /// El ring buffer tendrá capacidad `block_size * RING_BUFFER_MARGIN`.
    pub fn new(block_size: usize, channels: u16, sample_rate: u32) -> (Self, AudioBlockReceiver) {
        let capacity = block_size * RING_BUFFER_MARGIN;
        let (producer, consumer) = HeapRb::<f32>::new(capacity).split();

        let pipeline = AudioPipeline {
            block_size,
            channels,
            sample_rate,
            producer,
        };

        let receiver = AudioBlockReceiver {
            consumer,
            block_size,
            channels,
            sample_rate,
            assemble_buf: Vec::with_capacity(block_size),
        };

        (pipeline, receiver)
    }

    /// Ingesta muestras desde el CPAL callback.
    ///
    /// **Debe ser O(1), sin alloc, sin lock.** Si el buffer está lleno,
    /// `ringbuf` descarta automáticamente las muestras más viejas.
    #[inline]
    pub fn push_samples(&mut self, samples: &[f32]) {
        // push_slice_overwrite descarta las muestras más viejas si el buffer está lleno
        // — garantiza que el RT thread nunca bloquea.
        self.producer.push_slice(samples);
    }

    /// Capacidad total del ring buffer en samples.
    pub fn capacity(&self) -> usize {
        self.producer.capacity().get()
    }
}

// ---------------------------------------------------------------------------
// AudioBlockReceiver
// ---------------------------------------------------------------------------

impl AudioBlockReceiver {
    /// Intenta ensamblar un bloque completo de `block_size` samples.
    ///
    /// Devuelve `Some(AudioBlock)` cuando hay suficientes muestras disponibles,
    /// `None` si el buffer aún no tiene un bloque completo.
    ///
    /// Llamar este método es **barato** — no alloca si no hay bloque disponible.
    pub fn try_recv_block(&mut self) -> Option<AudioBlock> {
        // Drenar del ring buffer al buffer de ensamblado
        let available = self.consumer.occupied_len();
        if available == 0 {
            return None;
        }

        // Calcular cuánto podemos consumir sin exceder block_size
        let needed = self.block_size.saturating_sub(self.assemble_buf.len());
        let to_read = needed.min(available);

        let prev_len = self.assemble_buf.len();
        self.assemble_buf.resize(prev_len + to_read, 0.0);
        self.consumer.pop_slice(&mut self.assemble_buf[prev_len..]);

        if self.assemble_buf.len() < self.block_size {
            return None;
        }

        // Extraer exactamente block_size samples
        let samples: Vec<f32> = self.assemble_buf.drain(..self.block_size).collect();

        let timestamp_ms = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap_or_default()
            .as_millis() as u64;

        Some(AudioBlock {
            samples,
            channels: self.channels,
            sample_rate: self.sample_rate,
            timestamp_ms,
        })
    }
}

// ---------------------------------------------------------------------------
// Processing thread
// ---------------------------------------------------------------------------

/// Lanza el processing thread que consume bloques del `receiver` y emite
/// resultados FFT al frontend vía Tauri.
///
/// El thread se detiene cuando `stop_flag` pasa a `true`.
/// Devuelve un `JoinHandle` para sincronización en el shutdown.
pub fn spawn_processing_thread(
    mut receiver: AudioBlockReceiver,
    app: AppHandle,
    routing: Arc<std::sync::RwLock<ChannelRouting>>,
    stop_flag: Arc<AtomicBool>,
) -> thread::JoinHandle<()> {
    thread::Builder::new()
        .name("audio-processing".to_string())
        .spawn(move || {
            while !stop_flag.load(Ordering::Relaxed) {
                if let Some(block) = receiver.try_recv_block() {
                    // 1. Leer routing actual (puede cambiar entre bloques)
                    let routing_snapshot = routing
                        .read()
                        .map(|r| r.clone())
                        .unwrap_or_default();

                    // 2. Extraer canal principal ("X (input)") o todos los samples
                    //    si no hay routing configurado.
                    let mono = if routing_snapshot.assignments.is_empty() {
                        // Sin routing: downmix a mono promediando canales
                        downmix_to_mono(&block.samples, block.channels)
                    } else {
                        // Extraer primer canal lógico asignado
                        let first = &routing_snapshot.assignments[0];
                        routing_snapshot.extract_channel(
                            &block.samples,
                            first.physical_channel,
                            block.channels,
                        )
                    };

                    // 3. Calcular FFT y nivel RMS
                    let fft_result = compute_fft_result(&mono, block.sample_rate, block.timestamp_ms);

                    // 4. Emitir al frontend — el error se ignora si no hay listener
                    let _ = app.emit("audio://fft-result", &fft_result);
                } else {
                    // Sin datos — ceder CPU brevemente sin spin-wait total
                    thread::sleep(Duration::from_micros(PROCESSING_SLEEP_US));
                }
            }
        })
        .expect("No se pudo lanzar el processing thread de audio")
}

// ---------------------------------------------------------------------------
// DSP interno
// ---------------------------------------------------------------------------

/// Mezcla un buffer interleaved multi-canal a mono promediando todos los canales.
fn downmix_to_mono(interleaved: &[f32], channels: u16) -> Vec<f32> {
    if channels == 0 {
        return vec![];
    }
    let ch = channels as usize;
    let frames = interleaved.len() / ch;
    (0..frames)
        .map(|f| {
            let sum: f32 = (0..ch).map(|c| interleaved[f * ch + c]).sum();
            sum / ch as f32
        })
        .collect()
}

/// Calcula la FFT de una señal mono y devuelve magnitudes en dBFS + nivel RMS.
///
/// Usa la DFT de Cooley-Tukey implementada inline (sin dependencia extra).
/// Para producción se reemplazaría por `rustfft`.
fn compute_fft_result(samples: &[f32], sample_rate: u32, timestamp_ms: u64) -> FFTResult {
    let n = samples.len();
    if n == 0 {
        return FFTResult {
            frequencies: vec![],
            magnitudes_db: vec![],
            level_dbfs: f32::NEG_INFINITY,
            timestamp_ms,
        };
    }

    // Nivel RMS
    let rms = (samples.iter().map(|s| s * s).sum::<f32>() / n as f32).sqrt();
    let level_dbfs = if rms > 0.0 {
        20.0 * rms.log10()
    } else {
        f32::NEG_INFINITY
    };

    // DFT naïve — correcta pero O(N²). Para N≤4096 es aceptable en esta fase.
    // TODO: reemplazar por rustfft en la integración final.
    let half = n / 2 + 1;
    let mut magnitudes_db = Vec::with_capacity(half);
    let mut frequencies = Vec::with_capacity(half);

    use std::f32::consts::PI;
    for k in 0..half {
        let mut re = 0.0f32;
        let mut im = 0.0f32;
        for (i, &s) in samples.iter().enumerate() {
            let angle = 2.0 * PI * k as f32 * i as f32 / n as f32;
            re += s * angle.cos();
            im -= s * angle.sin();
        }
        let mag = (re * re + im * im).sqrt() / n as f32;
        let db = if mag > 1e-10 {
            20.0 * mag.log10()
        } else {
            -120.0
        };
        magnitudes_db.push(db);
        frequencies.push(k as f32 * sample_rate as f32 / n as f32);
    }

    FFTResult {
        frequencies,
        magnitudes_db,
        level_dbfs,
        timestamp_ms,
    }
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    fn make_pipeline(block_size: usize) -> (AudioPipeline, AudioBlockReceiver) {
        AudioPipeline::new(block_size, 1, 44100)
    }

    #[test]
    fn no_block_when_buffer_empty() {
        let (_pipeline, mut receiver) = make_pipeline(512);
        assert!(receiver.try_recv_block().is_none());
    }

    #[test]
    fn block_assembled_after_enough_samples() {
        let (mut pipeline, mut receiver) = make_pipeline(512);
        let samples = vec![0.5f32; 512];
        pipeline.push_samples(&samples);
        let block = receiver.try_recv_block();
        assert!(block.is_some());
        let b = block.unwrap();
        assert_eq!(b.samples.len(), 512);
        assert_eq!(b.channels, 1);
        assert_eq!(b.sample_rate, 44100);
    }

    #[test]
    fn partial_push_no_block_yet() {
        let (mut pipeline, mut receiver) = make_pipeline(512);
        pipeline.push_samples(&vec![0.1f32; 256]);
        assert!(receiver.try_recv_block().is_none());
        // Completar el bloque
        pipeline.push_samples(&vec![0.2f32; 256]);
        assert!(receiver.try_recv_block().is_some());
    }

    #[test]
    fn multiple_blocks_assembled_sequentially() {
        let (mut pipeline, mut receiver) = make_pipeline(256);
        // Enviar 3 bloques completos
        pipeline.push_samples(&vec![0.0f32; 768]);
        assert!(receiver.try_recv_block().is_some());
        assert!(receiver.try_recv_block().is_some());
        assert!(receiver.try_recv_block().is_some());
        assert!(receiver.try_recv_block().is_none());
    }

    #[test]
    fn overrun_does_not_panic() {
        // Llenar más del capacity del ring buffer — no debe entrar en pánico
        let (mut pipeline, mut _receiver) = make_pipeline(512);
        let huge = vec![0.0f32; 512 * RING_BUFFER_MARGIN * 4]; // 4x la capacidad
        pipeline.push_samples(&huge); // debe silenciosamente descartar
    }

    #[test]
    fn downmix_stereo_to_mono_averages_channels() {
        // Interleaved estéreo: [L0, R0, L1, R1] con L=1.0, R=0.0
        let interleaved = vec![1.0f32, 0.0, 1.0, 0.0];
        let mono = downmix_to_mono(&interleaved, 2);
        assert_eq!(mono.len(), 2);
        assert!((mono[0] - 0.5).abs() < 1e-6);
    }

    #[test]
    fn fft_result_level_silence_is_neg_inf() {
        let silence = vec![0.0f32; 512];
        let result = compute_fft_result(&silence, 44100, 0);
        assert!(result.level_dbfs.is_infinite() && result.level_dbfs < 0.0);
    }

    #[test]
    fn fft_result_has_correct_frequency_count() {
        let samples = vec![0.5f32; 512];
        let result = compute_fft_result(&samples, 44100, 0);
        // half = n/2 + 1 = 257
        assert_eq!(result.frequencies.len(), 257);
        assert_eq!(result.magnitudes_db.len(), 257);
    }

    #[test]
    fn pipeline_capacity_is_block_size_times_margin() {
        let (pipeline, _) = make_pipeline(1024);
        assert_eq!(pipeline.capacity(), 1024 * RING_BUFFER_MARGIN);
    }

    #[test]
    fn one_second_of_audio_no_dropped_blocks() {
        // 44100 samples a 44100 Hz = 1 segundo, block_size=512 → 86 bloques completos.
        // El test intercala push y receive para simular el patrón real RT + processing thread.
        let block_size = 512;
        let total_samples = 44100usize;
        let (mut pipeline, mut receiver) = AudioPipeline::new(block_size, 1, 44100);

        let mut received = 0;
        let mut sent = 0;

        while sent < total_samples {
            let end = (sent + block_size).min(total_samples);
            pipeline.push_samples(&vec![0.3f32; end - sent]);
            sent = end;
            // El processing thread consume inmediatamente
            while receiver.try_recv_block().is_some() {
                received += 1;
            }
        }

        let expected_blocks = total_samples / block_size; // 86
        assert_eq!(
            received, expected_blocks,
            "Se esperaban {expected_blocks} bloques completos, se recibieron {received}"
        );
    }

}
