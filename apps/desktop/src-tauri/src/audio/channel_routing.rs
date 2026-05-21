//! # Channel Routing
//!
//! Modelo de datos para el routing multi-canal de una interfaz de audio
//! profesional. Define qué canal físico del dispositivo alimenta cada señal
//! lógica de la app (X, Y, Reference, etc.).
//!
//! ## Uso típico por herramienta
//!
//! | Herramienta        | Canales lógicos                              |
//! |--------------------|----------------------------------------------|
//! | RTA                | `X (input)` → CH0                           |
//! | Transfer Function  | `X (input)` → CH0, `Y (output)` → CH1       |
//! | Coherence          | `X (reference)` → CH0, `Y (measurement)` → CH1 |
//!
//! ## Cambio en caliente
//! El routing puede cambiar mientras el stream está activo. `spawn_processing_thread`
//! lee el routing vía `Arc<RwLock<ChannelRouting>>` en cada bloque, por lo que
//! el cambio toma efecto en el próximo bloque sin reiniciar el stream.

use std::{collections::HashMap, sync::Mutex};

use serde::{Deserialize, Serialize};

// ---------------------------------------------------------------------------
// Tipos públicos
// ---------------------------------------------------------------------------

/// Asignación entre un canal lógico (nombre legible) y un canal físico (índice).
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ChannelAssignment {
    /// Nombre lógico del canal, ej. `"X (input)"`, `"Y (output)"`, `"Reference"`.
    pub logical_name: String,
    /// Índice 0-based del canal físico en el stream interleaved de CPAL.
    pub physical_channel: u16,
}

/// Configuración completa de routing para un stream de audio.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ChannelRouting {
    /// Lista de asignaciones lógico → físico.
    pub assignments: Vec<ChannelAssignment>,
    /// Total de canales físicos del dispositivo abierto.
    pub total_physical_channels: u16,
}

impl ChannelRouting {
    /// Crea un routing por defecto (sin asignaciones).
    pub fn new_empty() -> Self {
        Self {
            assignments: vec![],
            total_physical_channels: 0,
        }
    }

    /// Crea un routing estéreo estándar: CH0 → `"X (input)"`, CH1 → `"Y (output)"`.
    pub fn stereo_default() -> Self {
        Self {
            assignments: vec![
                ChannelAssignment {
                    logical_name: "X (input)".to_string(),
                    physical_channel: 0,
                },
                ChannelAssignment {
                    logical_name: "Y (output)".to_string(),
                    physical_channel: 1,
                },
            ],
            total_physical_channels: 2,
        }
    }

    /// Extrae un canal físico de un buffer interleaved.
    ///
    /// # Argumentos
    /// - `interleaved`: buffer de muestras en formato interleaved.
    /// - `channel_idx`: índice 0-based del canal a extraer.
    /// - `total_channels`: número total de canales en el stream (stride).
    ///
    /// # Ejemplo
    /// ```
    /// // Buffer estéreo: [L0, R0, L1, R1]
    /// let buf = vec![1.0f32, 2.0, 3.0, 4.0];
    /// let routing = ChannelRouting::new_empty();
    /// let left = routing.extract_channel(&buf, 0, 2);   // [1.0, 3.0]
    /// let right = routing.extract_channel(&buf, 1, 2);  // [2.0, 4.0]
    /// ```
    pub fn extract_channel(
        &self,
        interleaved: &[f32],
        channel_idx: u16,
        total_channels: u16,
    ) -> Vec<f32> {
        if total_channels == 0 {
            return vec![];
        }
        let ch = channel_idx as usize;
        let stride = total_channels as usize;

        // Si el canal pedido no existe en el buffer, devolver silencio.
        if ch >= stride {
            let frames = interleaved.len() / stride;
            return vec![0.0f32; frames];
        }

        interleaved
            .chunks_exact(stride)
            .map(|frame| frame[ch])
            .collect()
    }

    /// Extrae todos los canales asignados como mapa `logical_name → Vec<f32>`.
    ///
    /// Los canales físicos que estén fuera del rango del buffer se rellenan con
    /// silencio (0.0) para evitar pánico.
    pub fn extract_all(
        &self,
        interleaved: &[f32],
        total_channels: u16,
    ) -> HashMap<String, Vec<f32>> {
        self.assignments
            .iter()
            .map(|assignment| {
                let samples = self.extract_channel(
                    interleaved,
                    assignment.physical_channel,
                    total_channels,
                );
                (assignment.logical_name.clone(), samples)
            })
            .collect()
    }

    /// Devuelve el canal físico asignado a un nombre lógico, si existe.
    pub fn physical_channel_for(&self, logical_name: &str) -> Option<u16> {
        self.assignments
            .iter()
            .find(|a| a.logical_name == logical_name)
            .map(|a| a.physical_channel)
    }
}

impl Default for ChannelRouting {
    fn default() -> Self {
        Self::new_empty()
    }
}

// ---------------------------------------------------------------------------
// Estado de audio de la app (combina StreamManager + ChannelRouting)
// ---------------------------------------------------------------------------

/// Estado global de audio de la aplicación, almacenado como
/// `tauri::State<Mutex<AppAudioState>>`.
///
/// Combina el routing de canales con la referencia al pipeline activo.
pub struct AppAudioState {
    pub routing: ChannelRouting,
}

impl AppAudioState {
    pub fn new() -> Self {
        Self {
            routing: ChannelRouting::new_empty(),
        }
    }
}

impl Default for AppAudioState {
    fn default() -> Self {
        Self::new()
    }
}

// ---------------------------------------------------------------------------
// Tauri commands
// ---------------------------------------------------------------------------

/// Aplica una nueva configuración de routing de canales.
///
/// El cambio toma efecto en el próximo bloque de audio procesado.
///
/// Invocado desde Vue con:
/// ```js
/// invoke('set_channel_routing', { routing: { assignments: [...], total_physical_channels: 2 } })
/// ```
#[tauri::command]
pub async fn set_channel_routing(
    routing: ChannelRouting,
    state: tauri::State<'_, Mutex<AppAudioState>>,
) -> Result<(), String> {
    state
        .lock()
        .map_err(|e| format!("Error al adquirir lock de AppAudioState: {e}"))?
        .routing = routing;
    Ok(())
}

/// Devuelve la configuración de routing activa.
///
/// Invocado desde Vue con: `invoke('get_channel_routing')`
#[tauri::command]
pub async fn get_channel_routing(
    state: tauri::State<'_, Mutex<AppAudioState>>,
) -> Result<ChannelRouting, String> {
    Ok(state
        .lock()
        .map_err(|e| format!("Error al adquirir lock de AppAudioState: {e}"))?
        .routing
        .clone())
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn extract_left_channel_from_stereo() {
        let routing = ChannelRouting::new_empty();
        let buf = vec![1.0f32, 2.0, 3.0, 4.0]; // [L0, R0, L1, R1]
        let left = routing.extract_channel(&buf, 0, 2);
        assert_eq!(left, vec![1.0, 3.0]);
    }

    #[test]
    fn extract_right_channel_from_stereo() {
        let routing = ChannelRouting::new_empty();
        let buf = vec![1.0f32, 2.0, 3.0, 4.0];
        let right = routing.extract_channel(&buf, 1, 2);
        assert_eq!(right, vec![2.0, 4.0]);
    }

    #[test]
    fn extract_mono_channel() {
        let routing = ChannelRouting::new_empty();
        let buf = vec![0.5f32, 0.6, 0.7];
        let ch = routing.extract_channel(&buf, 0, 1);
        assert_eq!(ch, vec![0.5, 0.6, 0.7]);
    }

    #[test]
    fn out_of_range_channel_returns_silence() {
        let routing = ChannelRouting::new_empty();
        let buf = vec![1.0f32, 2.0]; // 1 frame estéreo
        let ch = routing.extract_channel(&buf, 5, 2); // canal 5 no existe
        assert_eq!(ch, vec![0.0]);
    }

    #[test]
    fn extract_all_returns_correct_map() {
        let routing = ChannelRouting {
            assignments: vec![
                ChannelAssignment {
                    logical_name: "X (input)".to_string(),
                    physical_channel: 0,
                },
                ChannelAssignment {
                    logical_name: "Y (output)".to_string(),
                    physical_channel: 1,
                },
            ],
            total_physical_channels: 2,
        };
        let buf = vec![1.0f32, 2.0, 3.0, 4.0]; // 2 frames estéreo
        let map = routing.extract_all(&buf, 2);

        assert_eq!(map["X (input)"], vec![1.0, 3.0]);
        assert_eq!(map["Y (output)"], vec![2.0, 4.0]);
    }

    #[test]
    fn physical_channel_for_returns_correct_index() {
        let routing = ChannelRouting::stereo_default();
        assert_eq!(routing.physical_channel_for("X (input)"), Some(0));
        assert_eq!(routing.physical_channel_for("Y (output)"), Some(1));
        assert_eq!(routing.physical_channel_for("nonexistent"), None);
    }

    #[test]
    fn eight_channel_interface_all_accessible() {
        let routing = ChannelRouting::new_empty();
        // Simula una interfaz de 8 canales con 1 frame
        let buf: Vec<f32> = (0..8).map(|i| i as f32).collect();
        for ch in 0..8u16 {
            let extracted = routing.extract_channel(&buf, ch, 8);
            assert_eq!(extracted.len(), 1);
            assert_eq!(extracted[0], ch as f32);
        }
    }

    #[test]
    fn routing_change_takes_effect_next_block() {
        // El routing se puede mutar y la extracción usa el valor actual
        let mut routing = ChannelRouting::stereo_default();
        let buf = vec![10.0f32, 20.0]; // 1 frame estéreo

        // Extrae CH0 (X input = 10.0)
        let ch = routing.physical_channel_for("X (input)").unwrap();
        assert_eq!(routing.extract_channel(&buf, ch, 2)[0], 10.0);

        // Cambiar routing: X ahora apunta a CH1
        routing.assignments[0].physical_channel = 1;
        let ch = routing.physical_channel_for("X (input)").unwrap();
        assert_eq!(routing.extract_channel(&buf, ch, 2)[0], 20.0);
    }
}
