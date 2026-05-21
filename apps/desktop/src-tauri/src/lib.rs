// Learn more about Tauri commands at https://tauri.app/develop/calling-rust/

pub mod audio;
pub mod commands;

use audio::{
    channel_routing::{get_channel_routing, set_channel_routing, AppAudioState},
    config_validator::{validate_stream_config, ConfigError},
    device_manager::{get_default_input_device, get_input_devices, get_output_devices},
    hotplug::{spawn_hotplug_watcher, DEFAULT_POLL_INTERVAL},
    stream_manager::{get_stream_state, start_audio_stream, stop_audio_stream, AudioStreamConfig, StreamManager},
};
use commands::dsp::{DspState, compute_fft_rt, process_block_rt};
use std::sync::{
    atomic::AtomicBool,
    Arc, Mutex,
};

// ---------------------------------------------------------------------------
// Tauri commands
// ---------------------------------------------------------------------------

#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

/// Valida una configuración de stream contra las capacidades del dispositivo.
///
/// Devuelve `Ok(())` si la config es válida, o un mensaje de error descriptivo.
/// La UI la usa para mostrar avisos antes de intentar abrir el stream.
///
/// Invocado desde Vue con:
/// ```js
/// invoke('validate_audio_config', { deviceId: '...', config: { ... } })
/// ```
#[tauri::command]
async fn validate_audio_config(
    device_id: String,
    config: AudioStreamConfig,
) -> Result<(), String> {
    // Re-enumerar dispositivos para obtener las capacidades actuales
    let devices = audio::device_manager::list_input_devices().map_err(|e| e.to_string())?;

    let device_info = devices
        .iter()
        .find(|d| d.id == device_id)
        .ok_or_else(|| format!("Dispositivo '{}' no encontrado", device_id))?;

    validate_stream_config(device_info, &config)
        .map(|_| ())
        .map_err(ConfigError::into)
}

/// Devuelve los sample rates soportados por un dispositivo de input.
///
/// La UI usa esta lista para poblar el selector de sample rate, mostrando
/// solo valores válidos para el dispositivo seleccionado.
///
/// Invocado desde Vue con: `invoke('get_supported_sample_rates', { deviceId })`
#[tauri::command]
async fn get_supported_sample_rates(device_id: String) -> Result<Vec<u32>, String> {
    let devices = audio::device_manager::list_input_devices().map_err(|e| e.to_string())?;

    let device_info = devices
        .iter()
        .find(|d| d.id == device_id)
        .ok_or_else(|| format!("Dispositivo '{}' no encontrado", device_id))?;

    Ok(audio::config_validator::supported_sample_rates(device_info))
}

// ---------------------------------------------------------------------------
// Punto de entrada de la app
// ---------------------------------------------------------------------------

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    // Stop flag compartido para el watcher de hot-plug
    let hotplug_stop = Arc::new(AtomicBool::new(false));
    let hotplug_stop_clone = Arc::clone(&hotplug_stop);

    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        // Estado global del StreamManager — un único stream activo a la vez.
        .manage(Mutex::new(StreamManager::new()))
        // Estado global de audio (routing de canales, etc.)
        .manage(Mutex::new(AppAudioState::new()))
        // Estado global del DSP para procesamiento en tiempo real
        .manage(Mutex::new(DspState::new()))
        // Stop flag del watcher de hot-plug (para shutdown limpio)
        .manage(hotplug_stop)
        .setup(move |app| {
            // Lanzar el watcher de hot-plug al iniciar la app.
            // El intervalo de 2 s cumple el criterio de aceptación (< 5 s).
            spawn_hotplug_watcher(
                app.handle().clone(),
                DEFAULT_POLL_INTERVAL,
                Arc::clone(&hotplug_stop_clone),
            );
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            greet,
            // #42 — Device manager
            get_input_devices,
            get_output_devices,
            get_default_input_device,
            // #43 — Stream lifecycle
            start_audio_stream,
            stop_audio_stream,
            get_stream_state,
            // #45 — Channel routing
            set_channel_routing,
            get_channel_routing,
            // #47/#48 — Hot-plug + validación
            validate_audio_config,
            get_supported_sample_rates,
            // #54 — Tauri command bridge (Rust DSP)
            process_block_rt,
            compute_fft_rt,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
