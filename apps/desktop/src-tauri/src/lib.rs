// Learn more about Tauri commands at https://tauri.app/develop/calling-rust/

pub mod audio;

use audio::{
    device_manager::{get_default_input_device, get_input_devices, get_output_devices},
    stream_manager::{get_stream_state, start_audio_stream, stop_audio_stream, StreamManager},
};
use std::sync::Mutex;

#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        // Estado global del StreamManager — un único stream activo a la vez.
        .manage(Mutex::new(StreamManager::new()))
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
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
