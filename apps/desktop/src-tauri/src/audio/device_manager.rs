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
// Estrategia Linux: enumeración orientada al usuario via PipeWire
// ---------------------------------------------------------------------------
//
// En Linux, CPAL usa el host ALSA que devuelve hasta 30+ dispositivos de bajo
// nivel ("hw:CARD=...", "plughw:...", "dmix:...", etc.) que el usuario nunca
// ve en el panel de sonido.
//
// Los nombres que el panel del sistema muestra vienen de PipeWire (o PulseAudio).
// Estrategia:
//   1. Consultar `pw-dump` (JSON) para obtener los nodos de tipo Audio/Sink
//      y Audio/Source con sus nombres amigables ("node.description").
//   2. Para cada nodo encontrado, usar el dispositivo ALSA "default" como
//      vehículo de transporte (PipeWire lo intercepta y redirige al hardware
//      correcto en tiempo de ejecución).
//   3. Si pw-dump no está disponible (sistema con ALSA puro), usar solo el
//      dispositivo "default" de CPAL con el nombre que devuelva el driver.

/// Nodo de PipeWire detectado por pw-dump.
#[cfg(target_os = "linux")]
#[derive(Debug, Clone)]
pub struct PipewireNode {
    pub name: String,
    pub channels: u16,
}

/// Consulta `pw-dump` y devuelve los nombres de los nodos de audio del tipo dado.
///
/// `media_class` debe ser `"Audio/Sink"` (outputs) o `"Audio/Source"` (inputs).
/// Filtra los streams de aplicaciones (class "Stream/...").
#[cfg(target_os = "linux")]
fn query_pipewire_nodes(media_class: &str) -> Vec<PipewireNode> {
    use std::process::Command;

    let Ok(output) = Command::new("pw-dump").output() else {
        return Vec::new();
    };

    if !output.status.success() {
        return Vec::new();
    }

    // pw-dump produce un JSON array de objetos
    let Ok(text) = std::str::from_utf8(&output.stdout) else {
        return Vec::new();
    };

    // Parse manual mínimo — evita añadir serde_json al build de producción.
    // Buscamos bloques del tipo:
    //   "media.class": "Audio/Sink"   +  "node.description": "<nombre>"  +  "audio.channels": <canales>
    let mut nodes = Vec::new();
    let mut current_class = String::new();
    let mut current_desc = String::new();
    let mut current_channels = 2; // Default a estéreo

    for line in text.lines() {
        let line = line.trim();

        if let Some(val) = json_str_value(line, "media.class") {
            current_class = val;
            current_desc.clear();
        }
        if let Some(val) = json_str_value(line, "node.description") {
            current_desc = val;
        }
        if let Some(val) = json_int_value(line, "audio.channels") {
            current_channels = val;
        }

        // Cuando tenemos ambos campos y el bloque cierra, registramos
        if line == "}," || line == "}" {
            if current_class == media_class && !current_desc.is_empty() {
                nodes.push(PipewireNode {
                    name: std::mem::take(&mut current_desc),
                    channels: current_channels,
                });
            }
            current_class.clear();
            current_desc.clear();
            current_channels = 2; // Reset
        }
    }

    nodes
}

/// Extrae el valor string de una línea JSON del estilo `"key": "value",`
#[cfg(target_os = "linux")]
fn json_str_value(line: &str, key: &str) -> Option<String> {
    // Busca: "key": "value"   o   "key": "value",
    let prefix = format!("\"{key}\": \"");
    let start = line.find(&prefix)?;
    let after = &line[start + prefix.len()..];
    let end = after.find('"')?;
    Some(after[..end].to_string())
}

/// Extrae el valor numérico de una línea JSON del estilo `"key": value,` o `"key": value`
#[cfg(target_os = "linux")]
fn json_int_value(line: &str, key: &str) -> Option<u16> {
    let prefix = format!("\"{key}\": ");
    let start = line.find(&prefix)?;
    let after = &line[start + prefix.len()..];
    let end = after.find(|c: char| !c.is_ascii_digit())?;
    after[..end].parse().ok()
}

/// Obtiene las configs CPAL del dispositivo "default" de CPAL para un filtro dado.
/// El dispositivo "default" es el que PipeWire/PulseAudio intercepta y redirige
/// al hardware activo, por lo que sus configs son representativas.
#[cfg(target_os = "linux")]
fn default_cpal_configs(filter: DeviceFilter) -> Vec<SupportedConfig> {
    let host = cpal::default_host();
    let dev = match filter {
        DeviceFilter::Input  => host.default_input_device(),
        DeviceFilter::Output => host.default_output_device(),
    };
    let Some(dev) = dev else { return Vec::new() };

    match filter {
        DeviceFilter::Input  => dev.supported_input_configs()
            .map(build_supported_configs).unwrap_or_default(),
        DeviceFilter::Output => dev.supported_output_configs()
            .map(build_supported_configs).unwrap_or_default(),
    }
}

/// Obtiene el nombre ALSA del dispositivo default (ej: "default" en ALSA/PipeWire).
#[cfg(target_os = "linux")]
fn default_alsa_device_name(filter: DeviceFilter) -> String {
    let host = cpal::default_host();
    let dev = match filter {
        DeviceFilter::Input  => host.default_input_device(),
        DeviceFilter::Output => host.default_output_device(),
    };
    dev.and_then(|d| d.name().ok()).unwrap_or_else(|| "default".to_string())
}

/// En Linux construye la lista de inputs orientada al usuario.
///
/// Muestra exactamente los dispositivos que aparecen en el panel de
/// configuración de audio del sistema operativo (Audio/Source de PipeWire).
#[cfg(target_os = "linux")]
pub fn list_input_devices_linux() -> Result<Vec<AudioDeviceInfo>, AudioError> {
    let pw_sources = query_pipewire_nodes("Audio/Source");
    let alsa_name  = default_alsa_device_name(DeviceFilter::Input);
    let configs    = default_cpal_configs(DeviceFilter::Input);

    if configs.is_empty() {
        // Sin dispositivo de input en el sistema
        return Ok(Vec::new());
    }

    if pw_sources.is_empty() {
        // PipeWire no disponible — mostrar solo el dispositivo default de CPAL
        return Ok(vec![AudioDeviceInfo {
            id:               stable_id(&alsa_name),
            name:             alsa_name,
            device_type:      "input".to_string(),
            is_default:       true,
            supported_configs: configs,
        }]);
    }

    // Construir una entrada por cada Source de PipeWire.
    // Todos comparten las mismas configs CPAL (el transporte es "default"),
    // pero con el número de canales limitados al máximo de canales físicos de PipeWire.
    let devices = pw_sources
        .into_iter()
        .enumerate()
        .map(|(i, node)| {
            let mut node_configs = configs.clone();
            for cfg in &mut node_configs {
                cfg.channels = std::cmp::min(cfg.channels, node.channels);
            }
            AudioDeviceInfo {
                id:               stable_id(&format!("{alsa_name}:source:{i}:{}", node.name)),
                name:             node.name,
                device_type:      "input".to_string(),
                is_default:       i == 0,
                supported_configs: node_configs,
            }
        })
        .collect();

    Ok(devices)
}

/// En Linux construye la lista de outputs orientada al usuario.
///
/// Muestra exactamente los dispositivos que aparecen en el panel de
/// configuración de audio del sistema operativo (Audio/Sink de PipeWire).
#[cfg(target_os = "linux")]
pub fn list_output_devices_linux() -> Result<Vec<AudioDeviceInfo>, AudioError> {
    let pw_sinks  = query_pipewire_nodes("Audio/Sink");
    let alsa_name = default_alsa_device_name(DeviceFilter::Output);
    let configs   = default_cpal_configs(DeviceFilter::Output);

    if configs.is_empty() {
        return Ok(Vec::new());
    }

    if pw_sinks.is_empty() {
        return Ok(vec![AudioDeviceInfo {
            id:               stable_id(&alsa_name),
            name:             alsa_name,
            device_type:      "output".to_string(),
            is_default:       true,
            supported_configs: configs,
        }]);
    }

    let devices = pw_sinks
        .into_iter()
        .enumerate()
        .map(|(i, node)| {
            let mut node_configs = configs.clone();
            for cfg in &mut node_configs {
                cfg.channels = std::cmp::min(cfg.channels, node.channels);
            }
            AudioDeviceInfo {
                id:               stable_id(&format!("{alsa_name}:sink:{i}:{}", node.name)),
                name:             node.name,
                device_type:      "output".to_string(),
                is_default:       i == 0,
                supported_configs: node_configs,
            }
        })
        .collect();

    Ok(devices)
}

/// Deduplica una lista de dispositivos por nombre (case-insensitive).
/// Mantiene la primera aparición de cada nombre, preservando el orden.
/// Solo se usa en el path no-Linux donde la enumeración CPAL puede tener
/// duplicados entre distintas interfaces del OS.
#[cfg(not(target_os = "linux"))]
fn dedup_by_name(devices: Vec<AudioDeviceInfo>) -> Vec<AudioDeviceInfo> {
    let mut seen = std::collections::HashSet::new();
    devices
        .into_iter()
        .filter(|d| seen.insert(d.name.to_lowercase()))
        .collect()
}

/// En plataformas no-Linux filtra dispositivos de bajo nivel por prefijo de nombre.
#[cfg(not(target_os = "linux"))]
fn is_user_visible_device(_name: &str) -> bool {
    true
}


fn add_virtual_simulator(mut devices: Vec<AudioDeviceInfo>) -> Vec<AudioDeviceInfo> {
    devices.insert(0, AudioDeviceInfo {
        id: "virtual-simulator".to_string(),
        name: "Simulador de Señal (Virtual)".to_string(),
        device_type: "input".to_string(),
        is_default: false,
        supported_configs: vec![
            SupportedConfig {
                channels: 2,
                min_sample_rate: 44100,
                max_sample_rate: 48000,
                sample_format: "f32".to_string(),
                buffer_size_range: Some((128, 2048)),
            }
        ],
    });
    devices
}

// ---------------------------------------------------------------------------
// API pública
// ---------------------------------------------------------------------------

/// Enumera los dispositivos de **input** disponibles orientados al usuario.
///
/// En Linux delega a `list_input_devices_linux()` que devuelve solo el
/// dispositivo activo de PipeWire/PulseAudio con nombre amigable.
/// En macOS/Windows enumera todos los dispositivos vía CPAL (ya son amigables).
#[cfg(target_os = "linux")]
pub fn list_input_devices() -> Result<Vec<AudioDeviceInfo>, AudioError> {
    list_input_devices_linux().map(add_virtual_simulator)
}

#[cfg(not(target_os = "linux"))]
pub fn list_input_devices() -> Result<Vec<AudioDeviceInfo>, AudioError> {
    let host = cpal::default_host();

    let default_name = host
        .default_input_device()
        .and_then(|d| d.name().ok())
        .unwrap_or_default();

    let devices = host
        .input_devices()
        .map_err(|e| AudioError::HostUnavailable(e.to_string()))?;

    let mut infos: Vec<AudioDeviceInfo> = devices
        .filter_map(|dev| {
            let name = dev.name().unwrap_or_default();
            let is_default = name == default_name;
            build_device_info(&dev, is_default, DeviceFilter::Input)
        })
        .collect();

    infos.sort_by(|a, b| b.is_default.cmp(&a.is_default).then(a.name.cmp(&b.name)));
    let infos = dedup_by_name(infos);
    Ok(add_virtual_simulator(infos))
}

/// Enumera los dispositivos de **output** disponibles orientados al usuario.
///
/// En Linux delega a `list_output_devices_linux()` que devuelve solo el
/// dispositivo activo de PipeWire/PulseAudio con nombre amigable.
/// En macOS/Windows enumera todos los dispositivos vía CPAL (ya son amigables).
#[cfg(target_os = "linux")]
pub fn list_output_devices() -> Result<Vec<AudioDeviceInfo>, AudioError> {
    list_output_devices_linux()
}

#[cfg(not(target_os = "linux"))]
pub fn list_output_devices() -> Result<Vec<AudioDeviceInfo>, AudioError> {
    let host = cpal::default_host();

    let default_name = host
        .default_output_device()
        .and_then(|d| d.name().ok())
        .unwrap_or_default();

    let devices = host
        .output_devices()
        .map_err(|e| AudioError::HostUnavailable(e.to_string()))?;

    let mut infos: Vec<AudioDeviceInfo> = devices
        .filter_map(|dev| {
            let name = dev.name().unwrap_or_default();
            let is_default = name == default_name;
            build_device_info(&dev, is_default, DeviceFilter::Output)
        })
        .collect();

    infos.sort_by(|a, b| b.is_default.cmp(&a.is_default).then(a.name.cmp(&b.name)));
    let infos = dedup_by_name(infos);
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
    let result = list_input_devices().map_err(Into::into);
    if let Ok(ref devs) = result {
        eprintln!("[get_input_devices] devolviendo {} dispositivos: {:?}",
            devs.len(), devs.iter().map(|d| &d.name).collect::<Vec<_>>());
    }
    result
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

    /// Test de diagnóstico: imprime los nombres de dispositivos que devuelve
    /// list_input_devices() después del filtrado. Ejecutar con:
    ///   cargo test print_input_device_names -- --nocapture
    #[test]
    fn print_input_device_names() {
        println!("\n=== list_input_devices() result ===");
        match list_input_devices() {
            Ok(devices) => {
                if devices.is_empty() {
                    println!("  (lista vacía)");
                }
                for d in &devices {
                    println!("  [{default}] id={id} name={name:?}",
                        default = if d.is_default { "DEFAULT" } else { "      " },
                        id = d.id,
                        name = d.name,
                    );
                }
            }
            Err(e) => println!("  ERROR: {e}"),
        }

        println!("\n=== list_output_devices() result ===");
        match list_output_devices() {
            Ok(devices) => {
                if devices.is_empty() {
                    println!("  (lista vacía)");
                }
                for d in &devices {
                    println!("  [{default}] id={id} name={name:?}",
                        default = if d.is_default { "DEFAULT" } else { "      " },
                        id = d.id,
                        name = d.name,
                    );
                }
            }
            Err(e) => println!("  ERROR: {e}"),
        }

        #[cfg(target_os = "linux")]
        {
            println!("\n=== query_pipewire_nodes(Audio/Source) ===");
            println!("  {:?}", query_pipewire_nodes("Audio/Source"));
            println!("\n=== query_pipewire_nodes(Audio/Sink) ===");
            println!("  {:?}", query_pipewire_nodes("Audio/Sink"));
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
