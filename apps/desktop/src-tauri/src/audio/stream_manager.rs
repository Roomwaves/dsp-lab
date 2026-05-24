//! # Audio Stream Manager
//!
//! Gestiona el ciclo de vida completo de un stream de audio: apertura, cierre y
//! reinicio ante cambios de configuración o errores de hardware.
//!
//! ## Diseño de threading
//!
//! ```text
//!  ┌────────────────────────────────────────────────────────┐
//!  │  Real-time thread (CPAL callback)                      │
//!  │  • lock-free: escribe en HeapRb<f32>                  │
//!  │  • nunca llama a Mutex::lock() en el hot path          │
//!  └────────────────────────┬───────────────────────────────┘
//!                           │  ringbuf (HeapRb)
//!  ┌────────────────────────▼───────────────────────────────┐
//!  │  Processing / UI thread                                │
//!  │  • consume muestras del ring buffer                    │
//!  │  • emite eventos Tauri al frontend                     │
//!  └────────────────────────────────────────────────────────┘
//! ```
//!
//! ## Política de errores
//! En caso de error de stream (ej. dispositivo desconectado):
//! 1. Se transiciona a `StreamState::Error`.
//! 2. Se emite el evento Tauri `audio://error` al frontend.
//! 3. **No** se intenta restart automático — el usuario decide.
//!
//! ## Invariante de unicidad
//! El `StreamManager` garantiza que nunca haya dos streams abiertos al mismo
//! tiempo. `start_stream` cierra el anterior antes de abrir uno nuevo.

use cpal::{
    traits::{DeviceTrait, HostTrait, StreamTrait},
    Stream,
};
use ringbuf::{traits::{Producer, Split}, HeapRb};
use serde::{Deserialize, Serialize};
use std::sync::Mutex;
use tauri::{AppHandle, Emitter};

use super::device_manager::AudioError;

// ---------------------------------------------------------------------------
// Constantes
// ---------------------------------------------------------------------------

/// Tamaño del ring buffer de audio en samples.
///
/// Con 48 kHz estéreo y un buffer de 512 samples se llenan ≈ 5 ms de audio.
/// 16 384 samples ≈ 341 ms — suficiente para absorber jitter de scheduling.
const RING_BUFFER_CAPACITY: usize = 16_384;

// ---------------------------------------------------------------------------
// Tipos públicos
// ---------------------------------------------------------------------------

/// Configuración que el frontend envía al abrir un stream.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AudioStreamConfig {
    /// ID del dispositivo a abrir (valor `id` de `AudioDeviceInfo`).
    pub device_id: String,
    /// Sample rate solicitado (Hz).
    pub sample_rate: u32,
    /// Número de canales a capturar (puede ser menor que los del dispositivo).
    pub channels: u16,
    /// Tamaño de buffer solicitado en samples.
    pub buffer_size: u32,
}

/// Bloque de audio producido por el RT callback.
///
/// Las muestras están intercaladas: `[ch0s0, ch1s0, ch0s1, ch1s1, …]`.
#[derive(Debug, Clone)]
pub struct AudioBlock {
    /// Muestras en formato f32 normalizado `[-1.0, 1.0]`.
    pub samples: Vec<f32>,
    /// Número de canales.
    pub channels: u16,
    /// Sample rate real del stream.
    pub sample_rate: u32,
}

/// Estado observable del stream manager.
#[derive(Debug, Clone)]
pub enum StreamState {
    /// No hay stream activo.
    Stopped,
    /// El stream está en proceso de apertura.
    Starting,
    /// El stream está activo con la configuración dada.
    Running(AudioStreamConfig),
    /// El stream tuvo un error — contiene el mensaje.
    Error(String),
}

impl StreamState {
    /// Serialización canónica para el Tauri command `get_stream_state`.
    pub fn to_status_string(&self) -> String {
        match self {
            StreamState::Stopped => "stopped".to_string(),
            StreamState::Starting => "starting".to_string(),
            StreamState::Running(_) => "running".to_string(),
            StreamState::Error(msg) => format!("error:{msg}"),
        }
    }
}

// ---------------------------------------------------------------------------
// StreamManager
// ---------------------------------------------------------------------------

/// Gestor de ciclo de vida de un stream de audio CPAL.
///
/// Debe instanciarse una sola vez y almacenarse como
/// `tauri::State<Mutex<StreamManager>>` en el proceso Tauri.
pub struct StreamManager {
    state: StreamState,
    /// El stream activo. Mantenerlo vivo previene que CPAL lo cierre.
    _stream: Option<Stream>,
    /// Última config con la que se abrió el stream (para `restart_stream`).
    last_config: Option<AudioStreamConfig>,
    processing_thread: Option<std::thread::JoinHandle<()>>,
    processing_stop: Option<std::sync::Arc<std::sync::atomic::AtomicBool>>,
}

// SAFETY: Stream contiene raw pointers internos de CPAL, pero el acceso
// siempre está serializado por el Mutex<StreamManager> en el estado Tauri.
unsafe impl Send for StreamManager {}

impl StreamManager {
    /// Crea un `StreamManager` en estado `Stopped`.
    pub fn new() -> Self {
        Self {
            state: StreamState::Stopped,
            _stream: None,
            last_config: None,
            processing_thread: None,
            processing_stop: None,
        }
    }

    /// Devuelve una referencia al estado actual del stream.
    pub fn state(&self) -> &StreamState {
        &self.state
    }

    /// Abre un nuevo stream con la `config` dada.
    ///
    /// Si había un stream anterior, se cierra primero (invariante de unicidad).
    /// El callback `on_error` recibe errores del driver.
    pub fn start_stream<R: tauri::Runtime + 'static>(
        &mut self,
        config: AudioStreamConfig,
        routing: std::sync::Arc<std::sync::RwLock<super::channel_routing::ChannelRouting>>,
        app: tauri::AppHandle<R>,
        on_error: impl Fn(AudioError) + Send + 'static,
    ) -> Result<(), AudioError> {
        // Cerrar stream anterior si existe.
        self.stop_stream()?;

        self.state = StreamState::Starting;

        // --- Localizar el dispositivo por su id estable ---
        let host = cpal::default_host();

        let device = host
            .input_devices()
            .map_err(|e| AudioError::HostUnavailable(e.to_string()))?
            .find(|d| {
                d.name()
                    .ok()
                    .map(|n| super::device_manager::stable_device_id(&n) == config.device_id)
                    .unwrap_or(false)
            })
            .or_else(|| host.default_input_device())
            .ok_or_else(|| {
                AudioError::DeviceNotFound(format!(
                    "No se encontró el dispositivo con id '{}'",
                    config.device_id
                ))
            })?;

        // --- Construir StreamConfig de CPAL ---
        let cpal_config = cpal::StreamConfig {
            channels: config.channels,
            sample_rate: cpal::SampleRate(config.sample_rate),
            buffer_size: cpal::BufferSize::Fixed(config.buffer_size),
        };

        // --- Crear ring buffer lock-free ---
        let (mut producer, consumer) = HeapRb::<f32>::new(RING_BUFFER_CAPACITY).split();

        let channels = config.channels;
        let sample_rate = config.sample_rate;
        let buffer_size = config.buffer_size;

        // --- Construir stream CPAL ---
        // El closure del RT thread solo escribe en el producer — lock-free.
        let stream = device
            .build_input_stream(
                &cpal_config,
                move |data: &[f32], _info: &cpal::InputCallbackInfo| {
                    // Intentar escribir en el ring buffer; si está lleno, descartar.
                    let _ = producer.push_slice(data);
                },
                move |err| {
                    on_error(AudioError::DeviceIntrospectionFailed(err.to_string()));
                },
                None,
            )
            .map_err(|e| {
                AudioError::DeviceIntrospectionFailed(format!("Error al construir stream: {e}"))
            })?;

        stream.play().map_err(|e| {
            AudioError::DeviceIntrospectionFailed(format!("Error al iniciar stream: {e}"))
        })?;

        // --- Iniciar processing thread ---
        let receiver = super::pipeline::AudioBlockReceiver::new(
            consumer,
            buffer_size as usize,
            channels,
            sample_rate,
        );

        let stop_flag = std::sync::Arc::new(std::sync::atomic::AtomicBool::new(false));
        let handle = super::pipeline::spawn_processing_thread(
            receiver,
            app,
            routing,
            std::sync::Arc::clone(&stop_flag),
        );

        self._stream = Some(stream);
        self.processing_thread = Some(handle);
        self.processing_stop = Some(stop_flag);
        self.last_config = Some(config.clone());
        self.state = StreamState::Running(config);

        Ok(())
    }

    /// Cierra el stream activo de forma ordenada.
    ///
    /// Es un no-op si no hay stream activo.
    pub fn stop_stream(&mut self) -> Result<(), AudioError> {
        // Detener el thread de procesamiento si existe
        if let Some(stop_flag) = self.processing_stop.take() {
            stop_flag.store(true, std::sync::atomic::Ordering::Relaxed);
        }
        if let Some(handle) = self.processing_thread.take() {
            let _ = handle.join();
        }

        // Soltar el stream hace que CPAL lo cierre gracefully.
        self._stream = None;
        self.state = StreamState::Stopped;
        Ok(())
    }

    /// Reinicia el stream con la misma configuración anterior.
    ///
    /// Útil para recovery manual tras un error. Falla si no se ha abierto
    /// ningún stream previamente.
    pub fn restart_stream<R: tauri::Runtime + 'static>(
        &mut self,
        routing: std::sync::Arc<std::sync::RwLock<super::channel_routing::ChannelRouting>>,
        app: tauri::AppHandle<R>,
    ) -> Result<(), AudioError> {
        let config = self
            .last_config
            .clone()
            .ok_or_else(|| AudioError::DeviceNotFound("No hay configuración previa para reiniciar".to_string()))?;

        self.start_stream(config, routing, app, |_| {})
    }

    /// Transiciona el estado a `Error` y registra el mensaje.
    ///
    /// Llamar este método **no** cierra el stream — se asume que ya falló.
    pub fn set_error(&mut self, msg: String) {
        if let Some(stop_flag) = self.processing_stop.take() {
            stop_flag.store(true, std::sync::atomic::Ordering::Relaxed);
        }
        if let Some(handle) = self.processing_thread.take() {
            let _ = handle.join();
        }
        self._stream = None;
        self.state = StreamState::Error(msg);
    }
}

impl Default for StreamManager {
    fn default() -> Self {
        Self::new()
    }
}

// ---------------------------------------------------------------------------
// Tauri commands
// ---------------------------------------------------------------------------

/// Abre un stream de audio con la configuración dada.
///
/// Cierra el stream anterior si ya había uno activo.
/// En caso de error de stream, emite el evento Tauri `audio://error`.
///
/// Invocado desde Vue con:
/// ```js
/// invoke('start_audio_stream', { config: { device_id, sample_rate, channels, buffer_size } })
/// ```
#[tauri::command]
pub async fn start_audio_stream(
    config: AudioStreamConfig,
    state: tauri::State<'_, Mutex<StreamManager>>,
    routing_state: tauri::State<'_, Mutex<super::channel_routing::AppAudioState>>,
    app: AppHandle,
) -> Result<(), String> {
    let mut mgr = state
        .lock()
        .map_err(|e| format!("Error al adquirir lock del StreamManager: {e}"))?;

    let routing = {
        let app_audio_state = routing_state
            .lock()
            .map_err(|e| format!("Error al adquirir lock de AppAudioState: {e}"))?;
        app_audio_state.routing.clone()
    };

    let app_for_error = app.clone();
    mgr.start_stream(
        config,
        routing,
        app,
        move |err| {
            let _ = app_for_error.emit("audio://error", err.to_string());
        },
    )
    .map_err(|e| e.to_string())
}

/// Cierra el stream de audio activo.
///
/// Invocado desde Vue con: `invoke('stop_audio_stream')`
#[tauri::command]
pub async fn stop_audio_stream(
    state: tauri::State<'_, Mutex<StreamManager>>,
) -> Result<(), String> {
    state
        .lock()
        .map_err(|e| format!("Error al adquirir lock del StreamManager: {e}"))?
        .stop_stream()
        .map_err(|e| e.to_string())
}

/// Devuelve el estado actual del stream como string.
///
/// Posibles valores: `"stopped"`, `"starting"`, `"running"`, `"error:<msg>"`.
///
/// Invocado desde Vue con: `invoke('get_stream_state')`
#[tauri::command]
pub async fn get_stream_state(
    state: tauri::State<'_, Mutex<StreamManager>>,
) -> Result<String, String> {
    Ok(state
        .lock()
        .map_err(|e| format!("Error al adquirir lock del StreamManager: {e}"))?
        .state()
        .to_status_string())
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn stream_manager_initial_state_is_stopped() {
        let mgr = StreamManager::new();
        assert!(
            matches!(mgr.state(), StreamState::Stopped),
            "El estado inicial debe ser Stopped"
        );
    }

    #[test]
    fn stop_stream_is_noop_when_stopped() {
        let mut mgr = StreamManager::new();
        // No debe entrar en pánico si no hay stream activo.
        assert!(mgr.stop_stream().is_ok());
        assert!(matches!(mgr.state(), StreamState::Stopped));
    }

    #[test]
    fn set_error_transitions_to_error_state() {
        let mut mgr = StreamManager::new();
        mgr.set_error("dispositivo desconectado".to_string());
        assert!(
            matches!(mgr.state(), StreamState::Error(_)),
            "Debe transicionar a Error"
        );
    }

    #[test]
    fn to_status_string_formats_correctly() {
        assert_eq!(StreamState::Stopped.to_status_string(), "stopped");
        assert_eq!(StreamState::Starting.to_status_string(), "starting");
        assert_eq!(
            StreamState::Error("boom".to_string()).to_status_string(),
            "error:boom"
        );
    }

    #[test]
    fn restart_without_previous_config_fails_gracefully() {
        let mut mgr = StreamManager::new();
        let routing = std::sync::Arc::new(std::sync::RwLock::new(super::super::channel_routing::ChannelRouting::new_empty()));
        let app = tauri::test::mock_app();
        let handle = app.handle().clone();
        let result = mgr.restart_stream(routing, handle);
        assert!(result.is_err(), "Restart sin config previa debe fallar");
    }
}
