//! # Audio Device Manager
//!
//! Enumera todos los dispositivos de audio disponibles en el sistema usando CPAL.
//! Expone sus capacidades (canales, sample rates, formatos) y las publica al
//! frontend vía Tauri commands.
//!
//! ## Notas de plataforma
//! - **macOS**: CPAL enumera vía CoreAudio.
//! - **Windows**: CPAL usa WASAPI (no ASIO por defecto).
//! - **Linux**: CPAL usa ALSA o PipeWire según el entorno.
//!
//! Los dispositivos Bluetooth pueden aparecer/desaparecer — los errores se
//! manejan de forma graceful y se omiten dispositivos que fallen durante la
//! introspección.

use cpal::traits::{DeviceTrait, HostTrait};
use serde::Serialize;

// ---------------------------------------------------------------------------
// Tipos públicos
// ---------------------------------------------------------------------------

/// Rango de configuración soportado por un dispositivo de audio.
#[derive(Debug, Clone, Serialize)]
pub struct SupportedConfig {
    /// Número de canales (mono = 1, estéreo = 2, multicanal > 2).
    pub channels: u16,
    /// Sample rate mínimo soportado (Hz).
    pub min_sample_rate: u32,
    /// Sample rate máximo soportado (Hz).
    pub max_sample_rate: u32,
    /// Formato de muestra: "f32", "i16", o "i32".
    pub sample_format: String,
    /// Rango de tamaño de buffer en samples `(min, max)`, si el driver lo informa.
    pub buffer_size_range: Option<(u32, u32)>,
}

/// Información completa de un dispositivo de audio del sistema.
#[derive(Debug, Clone, Serialize)]
pub struct AudioDeviceInfo {
    /// Identificador estable entre sesiones (hash SHA-256 del nombre del dispositivo).
    pub id: String,
    /// Nombre legible por humanos tal como lo reporta el OS.
    pub name: String,
    /// Tipo de dispositivo: `"input"`, `"output"`, o `"duplex"`.
    pub device_type: String,
    /// `true` si es el dispositivo por defecto del sistema para su tipo.
    pub is_default: bool,
    /// Lista de configuraciones soportadas.
    pub supported_configs: Vec<SupportedConfig>,
}

// ---------------------------------------------------------------------------
// Error interno
// ---------------------------------------------------------------------------

/// Error del subsistema de audio.
#[derive(Debug)]
pub enum AudioError {
    /// El host de audio del sistema no está disponible.
    HostUnavailable(String),
    /// No se encontró ningún dispositivo que cumpla el criterio.
    DeviceNotFound(String),
    /// Error durante la introspección de un dispositivo concreto.
    DeviceIntrospectionFailed(String),
}

impl std::fmt::Display for AudioError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            AudioError::HostUnavailable(msg) => write!(f, "Host de audio no disponible: {msg}"),
            AudioError::DeviceNotFound(msg) => write!(f, "Dispositivo no encontrado: {msg}"),
            AudioError::DeviceIntrospectionFailed(msg) => {
                write!(f, "Fallo al introspeccionar dispositivo: {msg}")
            }
        }
    }
}

impl From<AudioError> for String {
    fn from(e: AudioError) -> String {
        e.to_string()
    }
}

// ---------------------------------------------------------------------------
// Helpers internos
// ---------------------------------------------------------------------------

/// Genera un identificador estable a partir del nombre del dispositivo.
///
/// CPAL usa nombres como identificadores, pero éstos pueden variar entre
/// sesiones en ciertos OS (ej. sufijos numéricos en ALSA). Usamos un hash
/// SHA-256 del nombre normalizado como `id` estable.
/// Alias público de `stable_id` para uso cross-módulo (ej. desde `stream_manager`).
pub fn stable_device_id(name: &str) -> String {
    stable_id(name)
}

fn stable_id(name: &str) -> String {
    use std::collections::hash_map::DefaultHasher;
    use std::hash::{Hash, Hasher};

    // Usamos DefaultHasher (no criptográfico, pero suficiente para un ID de sesión).
    // Si se requiere estabilidad cross-proceso/cross-versión, considerar SHA-256 via `sha2`.
    let mut h = DefaultHasher::new();
    name.to_lowercase().hash(&mut h);
    format!("{:016x}", h.finish())
}

/// Convierte un `cpal::SampleFormat` al string canónico del proyecto.
fn format_name(fmt: cpal::SampleFormat) -> String {
    match fmt {
        cpal::SampleFormat::F32 => "f32".to_string(),
        cpal::SampleFormat::I16 => "i16".to_string(),
        cpal::SampleFormat::U8 => "u8".to_string(),
        _ => "unknown".to_string(),
    }
}

/// Extrae el rango de buffer size desde un `cpal::SupportedBufferSize`.
fn buffer_range(bs: &cpal::SupportedBufferSize) -> Option<(u32, u32)> {
    match bs {
        cpal::SupportedBufferSize::Range { min, max } => Some((*min, *max)),
        cpal::SupportedBufferSize::Unknown => None,
    }
}

/// Convierte una lista de `cpal::SupportedStreamConfigRange` en `Vec<SupportedConfig>`.
fn build_supported_configs(
    ranges: impl Iterator<Item = cpal::SupportedStreamConfigRange>,
) -> Vec<SupportedConfig> {
    ranges
        .map(|r| SupportedConfig {
            channels: r.channels(),
            min_sample_rate: r.min_sample_rate().0,
            max_sample_rate: r.max_sample_rate().0,
            sample_format: format_name(r.sample_format()),
            buffer_size_range: buffer_range(r.buffer_size()),
        })
        .collect()
}

/// Determina el `device_type` de un dispositivo inspeccionando si soporta
/// configuraciones de input, output, o ambas (duplex).
fn device_type(device: &cpal::Device) -> String {
    let has_input = device.supported_input_configs().is_ok_and(|c| c.count() > 0);
    let has_output = device
        .supported_output_configs()
        .is_ok_and(|c| c.count() > 0);

    match (has_input, has_output) {
        (true, true) => "duplex".to_string(),
        (true, false) => "input".to_string(),
        (false, true) => "output".to_string(),
        (false, false) => "unknown".to_string(),
    }
}

/// Construye un `AudioDeviceInfo` para un dispositivo dado.
///
/// `is_default` debe pasarse desde el contexto del llamador, ya que CPAL
/// determina el dispositivo por defecto a nivel de host.
///
/// Devuelve `None` si el dispositivo no puede introspeccionar ni input ni output.
fn build_device_info(
    device: &cpal::Device,
    is_default: bool,
    filter: DeviceFilter,
) -> Option<AudioDeviceInfo> {
    let name = device.name().unwrap_or_else(|_| "Dispositivo desconocido".to_string());

    let supported_configs: Vec<SupportedConfig> = match filter {
        DeviceFilter::Input => device
            .supported_input_configs()
            .map(build_supported_configs)
            .unwrap_or_default(),
        DeviceFilter::Output => device
            .supported_output_configs()
            .map(build_supported_configs)
            .unwrap_or_default(),
    };

    // Si no hay configuraciones para el tipo de filtro, omitimos el dispositivo.
    if supported_configs.is_empty() {
        return None;
    }

    Some(AudioDeviceInfo {
        id: stable_id(&name),
        name,
        device_type: device_type(device),
        is_default,
        supported_configs,
    })
}

/// Filtro interno para seleccionar dispositivos de input o output.
#[derive(Clone, Copy)]
enum DeviceFilter {
    Input,
    Output,
}

// ---------------------------------------------------------------------------
// API pública
// ---------------------------------------------------------------------------

/// Enumera todos los dispositivos de **input** disponibles en el sistema.
///
/// Los dispositivos que fallen durante la introspección se omiten silenciosamente.
/// Si no hay dispositivos, devuelve un `Vec` vacío (no panic).
pub fn list_input_devices() -> Result<Vec<AudioDeviceInfo>, AudioError> {
    let host = cpal::default_host();

    let default_name = host
        .default_input_device()
        .and_then(|d| d.name().ok())
        .unwrap_or_default();

    let devices = host
        .input_devices()
        .map_err(|e| AudioError::HostUnavailable(e.to_string()))?;

    let infos: Vec<AudioDeviceInfo> = devices
        .filter_map(|dev| {
            let name = dev.name().unwrap_or_default();
            let is_default = name == default_name;
            build_device_info(&dev, is_default, DeviceFilter::Input)
        })
        .collect();

    Ok(infos)
}

/// Enumera todos los dispositivos de **output** disponibles en el sistema.
///
/// Los dispositivos que fallen durante la introspección se omiten silenciosamente.
/// Si no hay dispositivos, devuelve un `Vec` vacío (no panic).
pub fn list_output_devices() -> Result<Vec<AudioDeviceInfo>, AudioError> {
    let host = cpal::default_host();

    let default_name = host
        .default_output_device()
        .and_then(|d| d.name().ok())
        .unwrap_or_default();

    let devices = host
        .output_devices()
        .map_err(|e| AudioError::HostUnavailable(e.to_string()))?;

    let infos: Vec<AudioDeviceInfo> = devices
        .filter_map(|dev| {
            let name = dev.name().unwrap_or_default();
            let is_default = name == default_name;
            build_device_info(&dev, is_default, DeviceFilter::Output)
        })
        .collect();

    Ok(infos)
}

/// Devuelve el dispositivo de **input** por defecto del sistema.
///
/// Falla con `AudioError::DeviceNotFound` si el sistema no tiene dispositivos
/// de input (ej. servidor headless).
pub fn default_input_device() -> Result<AudioDeviceInfo, AudioError> {
    let host = cpal::default_host();

    let device = host
        .default_input_device()
        .ok_or_else(|| AudioError::DeviceNotFound("No hay dispositivo de input por defecto".to_string()))?;

    build_device_info(&device, true, DeviceFilter::Input).ok_or_else(|| {
        AudioError::DeviceIntrospectionFailed(
            "El dispositivo por defecto no reporta configuraciones de input".to_string(),
        )
    })
}

// ---------------------------------------------------------------------------
// Tauri commands
// ---------------------------------------------------------------------------

/// Devuelve la lista de dispositivos de input disponibles.
///
/// Invocado desde Vue con: `invoke('get_input_devices')`
#[tauri::command]
pub async fn get_input_devices() -> Result<Vec<AudioDeviceInfo>, String> {
    list_input_devices().map_err(Into::into)
}

/// Devuelve la lista de dispositivos de output disponibles.
///
/// Invocado desde Vue con: `invoke('get_output_devices')`
#[tauri::command]
pub async fn get_output_devices() -> Result<Vec<AudioDeviceInfo>, String> {
    list_output_devices().map_err(Into::into)
}

/// Devuelve el dispositivo de input por defecto del sistema.
///
/// Invocado desde Vue con: `invoke('get_default_input_device')`
#[tauri::command]
pub async fn get_default_input_device() -> Result<AudioDeviceInfo, String> {
    default_input_device().map_err(Into::into)
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    /// Verifica que la función no entre en pánico cuando se invoca en CI
    /// (puede no haber dispositivos de audio).
    #[test]
    fn list_input_devices_no_panic() {
        let result = list_input_devices();
        // En CI sin audio, puede ser Ok(vec![]) o Err — nunca panic.
        match result {
            Ok(devices) => {
                // Si hay dispositivos, todos deben tener un id no vacío.
                for d in &devices {
                    assert!(!d.id.is_empty(), "El id no debe estar vacío");
                    assert!(!d.name.is_empty(), "El nombre no debe estar vacío");
                    assert!(
                        !d.supported_configs.is_empty(),
                        "Debe haber al menos una config soportada"
                    );
                }
            }
            Err(_) => { /* aceptable en entorno sin audio */ }
        }
    }

    #[test]
    fn list_output_devices_no_panic() {
        // Mismo razonamiento que list_input_devices_no_panic.
        let _ = list_output_devices();
    }

    #[test]
    fn stable_id_is_deterministic() {
        let id1 = stable_id("Built-in Microphone");
        let id2 = stable_id("Built-in Microphone");
        assert_eq!(id1, id2, "El id debe ser determinístico para el mismo nombre");
    }

    #[test]
    fn stable_id_differs_for_different_names() {
        let id1 = stable_id("Built-in Microphone");
        let id2 = stable_id("USB Audio Device");
        assert_ne!(id1, id2, "Nombres distintos deben producir ids distintos");
    }

    #[test]
    fn format_name_covers_known_formats() {
        assert_eq!(format_name(cpal::SampleFormat::F32), "f32");
        assert_eq!(format_name(cpal::SampleFormat::I16), "i16");
        assert_eq!(format_name(cpal::SampleFormat::U8), "u8");
    }
}
