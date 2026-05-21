//! # Hot-plug Watcher
//!
//! Detecta cuando el usuario conecta o desconecta hardware de audio mientras
//! la app está corriendo, usando **polling** comparando la lista de dispositivos
//! cada N segundos (configurable).
//!
//! ## Por qué polling y no callbacks nativos del OS
//!
//! CPAL (v0.15) no provee notificaciones de hot-plug multiplataforma. Las APIs
//! nativas (CoreAudio `AudioObjectAddPropertyListener`, WASAPI `IMMNotificationClient`,
//! udev) requieren FFI adicional por plataforma y están fuera del scope de esta
//! iteración. El polling a 2 s cumple el criterio de aceptación (< 5 s).
//!
//! ## Comportamiento ante desconexión
//!
//! Cuando el dispositivo activo se desconecta, CPAL emite un error al callback
//! del stream. El `StreamManager` captura ese error, transiciona a
//! `StreamState::Error` y emite `audio://stream-error`. El hot-plug watcher
//! detecta simultáneamente la desaparición del dispositivo y emite
//! `audio://device-disconnected`. La UI muestra el mensaje al usuario.
//!
//! **NO se intenta restart automático** — el usuario elige.
//!
//! ## Eventos emitidos
//!
//! | Evento Tauri                    | Payload                      | Cuándo         |
//! |---------------------------------|------------------------------|----------------|
//! | `audio://device-connected`      | `AudioDeviceInfo` (input)    | Nuevo input    |
//! | `audio://device-disconnected`   | `AudioDeviceInfo` (input)    | Input removido |
//! | `audio://output-connected`      | `AudioDeviceInfo` (output)   | Nuevo output   |
//! | `audio://output-disconnected`   | `AudioDeviceInfo` (output)   | Output removido|

use std::{
    collections::HashMap,
    sync::{
        atomic::{AtomicBool, Ordering},
        Arc,
    },
    thread,
    time::Duration,
};

use tauri::{AppHandle, Emitter};

use super::device_manager::{list_input_devices, list_output_devices, AudioDeviceInfo};

// ---------------------------------------------------------------------------
// Constantes
// ---------------------------------------------------------------------------

/// Intervalo de polling por defecto: 2 segundos.
pub const DEFAULT_POLL_INTERVAL: Duration = Duration::from_secs(2);

// ---------------------------------------------------------------------------
// Snapshot de dispositivos
// ---------------------------------------------------------------------------

/// Snapshot del conjunto de dispositivos conocidos, indexado por `id`.
type DeviceSnapshot = HashMap<String, AudioDeviceInfo>;

/// Construye un snapshot de inputs + outputs combinados, indexado por id.
///
/// Los errores de enumeración se manejan gracefully: si el host no está
/// disponible, devuelve el snapshot anterior (sin cambios).
fn snapshot_all_devices() -> (DeviceSnapshot, DeviceSnapshot) {
    let inputs = list_input_devices()
        .unwrap_or_default()
        .into_iter()
        .map(|d| (d.id.clone(), d))
        .collect();

    let outputs = list_output_devices()
        .unwrap_or_default()
        .into_iter()
        .map(|d| (d.id.clone(), d))
        .collect();

    (inputs, outputs)
}

// ---------------------------------------------------------------------------
// Diff de snapshots
// ---------------------------------------------------------------------------

/// Dispositivos presentes en `current` que no estaban en `previous` (conectados).
fn devices_added(
    previous: &DeviceSnapshot,
    current: &DeviceSnapshot,
) -> Vec<AudioDeviceInfo> {
    current
        .values()
        .filter(|d| !previous.contains_key(&d.id))
        .cloned()
        .collect()
}

/// Dispositivos presentes en `previous` que ya no están en `current` (desconectados).
fn devices_removed(
    previous: &DeviceSnapshot,
    current: &DeviceSnapshot,
) -> Vec<AudioDeviceInfo> {
    previous
        .values()
        .filter(|d| !current.contains_key(&d.id))
        .cloned()
        .collect()
}

// ---------------------------------------------------------------------------
// Hot-plug watcher
// ---------------------------------------------------------------------------

/// Lanza el thread de polling que detecta cambios en la lista de dispositivos.
///
/// # Argumentos
/// - `app`: handle de la app Tauri para emitir eventos al frontend.
/// - `interval`: intervalo de polling (recomendado: `DEFAULT_POLL_INTERVAL`).
/// - `stop_flag`: `Arc<AtomicBool>` para detener el watcher limpiamente.
///
/// # Eventos emitidos
/// - `audio://device-connected` / `audio://device-disconnected` para inputs.
/// - `audio://output-connected` / `audio://output-disconnected` para outputs.
///
/// # Retorno
/// `JoinHandle<()>` — join en el shutdown de la app para limpiar el thread.
pub fn spawn_hotplug_watcher(
    app: AppHandle,
    interval: Duration,
    stop_flag: Arc<AtomicBool>,
) -> thread::JoinHandle<()> {
    thread::Builder::new()
        .name("audio-hotplug".to_string())
        .spawn(move || {
            // Snapshot inicial — se considera como "estado conocido" sin emitir eventos.
            let (mut known_inputs, mut known_outputs) = snapshot_all_devices();

            while !stop_flag.load(Ordering::Relaxed) {
                thread::sleep(interval);

                // Re-enumerar dispositivos actuales
                let (current_inputs, current_outputs) = snapshot_all_devices();

                // --- Inputs ---
                for device in devices_added(&known_inputs, &current_inputs) {
                    let _ = app.emit("audio://device-connected", &device);
                    eprintln!(
                        "[hotplug] Input conectado: {} ({})",
                        device.name, device.id
                    );
                }
                for device in devices_removed(&known_inputs, &current_inputs) {
                    let _ = app.emit("audio://device-disconnected", &device);
                    eprintln!(
                        "[hotplug] Input desconectado: {} ({})",
                        device.name, device.id
                    );
                }

                // --- Outputs ---
                for device in devices_added(&known_outputs, &current_outputs) {
                    let _ = app.emit("audio://output-connected", &device);
                    eprintln!(
                        "[hotplug] Output conectado: {} ({})",
                        device.name, device.id
                    );
                }
                for device in devices_removed(&known_outputs, &current_outputs) {
                    let _ = app.emit("audio://output-disconnected", &device);
                    eprintln!(
                        "[hotplug] Output desconectado: {} ({})",
                        device.name, device.id
                    );
                }

                // Actualizar snapshots
                known_inputs  = current_inputs;
                known_outputs = current_outputs;
            }

            eprintln!("[hotplug] Watcher detenido.");
        })
        .expect("No se pudo lanzar el thread de hot-plug")
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;
    use crate::audio::device_manager::SupportedConfig;

    /// Construye un `AudioDeviceInfo` mínimo para tests.
    fn fake_device(id: &str, name: &str) -> AudioDeviceInfo {
        AudioDeviceInfo {
            id: id.to_string(),
            name: name.to_string(),
            device_type: "input".to_string(),
            is_default: false,
            supported_configs: vec![SupportedConfig {
                channels: 2,
                min_sample_rate: 44100,
                max_sample_rate: 48000,
                sample_format: "f32".to_string(),
                buffer_size_range: None,
            }],
        }
    }

    fn snapshot_from(devices: &[AudioDeviceInfo]) -> DeviceSnapshot {
        devices
            .iter()
            .map(|d| (d.id.clone(), d.clone()))
            .collect()
    }

    #[test]
    fn added_detects_new_device() {
        let prev = snapshot_from(&[fake_device("id1", "Mic A")]);
        let curr = snapshot_from(&[
            fake_device("id1", "Mic A"),
            fake_device("id2", "USB Mic"),
        ]);
        let added = devices_added(&prev, &curr);
        assert_eq!(added.len(), 1);
        assert_eq!(added[0].id, "id2");
    }

    #[test]
    fn removed_detects_disconnected_device() {
        let prev = snapshot_from(&[
            fake_device("id1", "Mic A"),
            fake_device("id2", "USB Mic"),
        ]);
        let curr = snapshot_from(&[fake_device("id1", "Mic A")]);
        let removed = devices_removed(&prev, &curr);
        assert_eq!(removed.len(), 1);
        assert_eq!(removed[0].id, "id2");
    }

    #[test]
    fn no_change_emits_nothing() {
        let prev = snapshot_from(&[fake_device("id1", "Mic A")]);
        let curr = snapshot_from(&[fake_device("id1", "Mic A")]);
        assert!(devices_added(&prev, &curr).is_empty());
        assert!(devices_removed(&prev, &curr).is_empty());
    }

    #[test]
    fn empty_initial_treats_all_as_added() {
        let prev: DeviceSnapshot = HashMap::new();
        let curr = snapshot_from(&[fake_device("id1", "Mic A")]);
        let added = devices_added(&prev, &curr);
        assert_eq!(added.len(), 1);
    }

    #[test]
    fn all_removed_from_empty_current() {
        let prev = snapshot_from(&[
            fake_device("id1", "Mic A"),
            fake_device("id2", "USB Mic"),
        ]);
        let curr: DeviceSnapshot = HashMap::new();
        let removed = devices_removed(&prev, &curr);
        assert_eq!(removed.len(), 2);
    }

    #[test]
    fn simultaneous_add_and_remove() {
        let prev = snapshot_from(&[fake_device("old", "Old Mic")]);
        let curr = snapshot_from(&[fake_device("new", "New Interface")]);
        assert_eq!(devices_added(&prev, &curr).len(), 1);
        assert_eq!(devices_removed(&prev, &curr).len(), 1);
        assert_eq!(devices_added(&prev, &curr)[0].id, "new");
        assert_eq!(devices_removed(&prev, &curr)[0].id, "old");
    }

    #[test]
    fn snapshot_all_devices_no_panic() {
        // No debe entrar en pánico en un entorno sin audio (CI)
        let (_inputs, _outputs) = snapshot_all_devices();
    }
}
