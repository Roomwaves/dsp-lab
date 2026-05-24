//! # Config Validator
//!
//! Valida que una `AudioStreamConfig` sea compatible con las capacidades del
//! dispositivo de audio **antes** de intentar abrir el stream. Un stream con
//! configuración inválida provoca errores oscuros o panics en CPAL.
//!
//! ## Responsabilidades
//!
//! 1. Verificar que `sample_rate` cae dentro del rango soportado por el device.
//! 2. Verificar que `channels` ≤ canales máximos del device.
//! 3. Verificar que `buffer_size` cae dentro del rango soportado (si está informado).
//! 4. Seleccionar la `SupportedConfig` más cercana al formato `f32` (preferido).
//! 5. Retornar un `cpal::StreamConfig` listo para pasar a `build_input_stream`.
//!
//! ## Uso en `stream_manager.rs`
//!
//! ```ignore
//! let cpal_config = validate_stream_config(&device_info, &config)?;
//! device.build_input_stream(&cpal_config, data_cb, err_cb, None)?;
//! ```

use cpal::SampleRate;
use serde::Serialize;

use super::device_manager::{AudioDeviceInfo, SupportedConfig};
use super::stream_manager::AudioStreamConfig;

// ---------------------------------------------------------------------------
// ConfigError
// ---------------------------------------------------------------------------

/// Error descriptivo de validación de configuración de stream.
///
/// Todos los variantes incluyen los valores pedidos y los límites del dispositivo
/// para que la UI pueda mostrar un mensaje útil al usuario.
#[derive(Debug, Clone, PartialEq, Serialize)]
pub enum ConfigError {
    /// El sample rate pedido está fuera del rango soportado.
    UnsupportedSampleRate {
        /// Sample rate pedido (Hz).
        requested: u32,
        /// Mínimo soportado por el dispositivo (Hz).
        min_supported: u32,
        /// Máximo soportado por el dispositivo (Hz).
        max_supported: u32,
    },
    /// Se pidieron más canales de los que tiene el dispositivo.
    TooManyChannels {
        /// Canales máximos del dispositivo.
        device_max: u16,
        /// Canales pedidos en la config.
        requested: u16,
    },
    /// El buffer size está fuera del rango soportado (solo cuando el device lo informa).
    UnsupportedBufferSize {
        /// Buffer size pedido (samples).
        requested: u32,
        /// Mínimo soportado.
        min_supported: u32,
        /// Máximo soportado.
        max_supported: u32,
    },
    /// El dispositivo no reporta ninguna configuración soportada.
    NoSupportedConfigs,
}

impl std::fmt::Display for ConfigError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            ConfigError::UnsupportedSampleRate { requested, min_supported, max_supported } => {
                write!(
                    f,
                    "Sample rate {requested} Hz no soportado. Rango del dispositivo: {min_supported}–{max_supported} Hz"
                )
            }
            ConfigError::TooManyChannels { device_max, requested } => {
                write!(
                    f,
                    "El dispositivo tiene {device_max} canales, no se pueden abrir {requested}"
                )
            }
            ConfigError::UnsupportedBufferSize { requested, min_supported, max_supported } => {
                write!(
                    f,
                    "Buffer size {requested} samples fuera del rango soportado: {min_supported}–{max_supported}"
                )
            }
            ConfigError::NoSupportedConfigs => {
                write!(f, "El dispositivo no reporta configuraciones soportadas")
            }
        }
    }
}

impl From<ConfigError> for String {
    fn from(e: ConfigError) -> String {
        e.to_string()
    }
}

// ---------------------------------------------------------------------------
// Funciones de consulta pública (para la UI)
// ---------------------------------------------------------------------------

/// Devuelve los sample rates estándar soportados por un dispositivo de input.
///
/// La UI usa esta lista para poblar el selector de sample rate mostrando solo
/// valores válidos para el dispositivo activo.
///
/// Los rates candidatos son los más comunes en audio profesional.
/// Se incluye un rate si cae dentro del rango `[min_sample_rate, max_sample_rate]`
/// de **cualquier** `SupportedConfig` del dispositivo.
pub fn supported_sample_rates(device: &AudioDeviceInfo) -> Vec<u32> {
    // Rates candidatos en orden ascendente
    const CANDIDATE_RATES: &[u32] = &[8_000, 11_025, 16_000, 22_050, 32_000, 44_100, 48_000, 88_200, 96_000, 176_400, 192_000];

    if device.supported_configs.is_empty() {
        return vec![];
    }

    CANDIDATE_RATES
        .iter()
        .copied()
        .filter(|&rate| {
            device.supported_configs.iter().any(|cfg| {
                rate >= cfg.min_sample_rate && rate <= cfg.max_sample_rate
            })
        })
        .collect()
}

/// Devuelve el número máximo de canales soportado por el dispositivo
/// (el máximo entre todas sus `SupportedConfig`).
pub fn max_supported_channels(device: &AudioDeviceInfo) -> u16 {
    device
        .supported_configs
        .iter()
        .map(|c| c.channels)
        .max()
        .unwrap_or(0)
}

/// Devuelve el rango de buffer size soportado `(min, max)` por el dispositivo,
/// tomando la intersección de todos los rangos reportados. Devuelve `None`
/// si ninguna config reporta un rango concreto.
pub fn supported_buffer_size_range(device: &AudioDeviceInfo) -> Option<(u32, u32)> {
    let ranges: Vec<(u32, u32)> = device
        .supported_configs
        .iter()
        .filter_map(|c| c.buffer_size_range)
        .collect();

    if ranges.is_empty() {
        return None;
    }

    // Unión de rangos: el min más pequeño y el max más grande
    let min = ranges.iter().map(|(lo, _)| *lo).min().unwrap();
    let max = ranges.iter().map(|(_, hi)| *hi).max().unwrap();
    Some((min, max))
}

// ---------------------------------------------------------------------------
// Validación principal
// ---------------------------------------------------------------------------

/// Valida que `config` sea compatible con las capacidades de `device_info`
/// y devuelve un `cpal::StreamConfig` listo para usar.
///
/// ## Orden de validación
/// 1. El dispositivo debe tener al menos una `SupportedConfig`.
/// 2. `config.sample_rate` debe caer en el rango de alguna `SupportedConfig`.
/// 3. `config.channels` ≤ canales máximos del dispositivo.
/// 4. Si el driver informa un rango de buffer size, `config.buffer_size` debe respetarlo.
///
/// ## Selección de `SupportedConfig`
/// Se selecciona la config del dispositivo que:
/// - Cubre `config.sample_rate` y `config.channels`.
/// - Prefiere formato `f32` sobre los demás.
pub fn validate_stream_config(
    device_info: &AudioDeviceInfo,
    config: &AudioStreamConfig,
) -> Result<cpal::StreamConfig, ConfigError> {
    if device_info.supported_configs.is_empty() {
        return Err(ConfigError::NoSupportedConfigs);
    }

    // 1. Verificar sample rate
    let rate_ok = device_info.supported_configs.iter().any(|c| {
        config.sample_rate >= c.min_sample_rate && config.sample_rate <= c.max_sample_rate
    });

    if !rate_ok {
        let min_sr = device_info
            .supported_configs
            .iter()
            .map(|c| c.min_sample_rate)
            .min()
            .unwrap();
        let max_sr = device_info
            .supported_configs
            .iter()
            .map(|c| c.max_sample_rate)
            .max()
            .unwrap();
        return Err(ConfigError::UnsupportedSampleRate {
            requested: config.sample_rate,
            min_supported: min_sr,
            max_supported: max_sr,
        });
    }

    // 2. Verificar canales
    let max_ch = max_supported_channels(device_info);
    if config.channels > max_ch {
        return Err(ConfigError::TooManyChannels {
            device_max: max_ch,
            requested: config.channels,
        });
    }

    // 3. Verificar buffer size (solo si el driver lo informa)
    if let Some((min_buf, max_buf)) = supported_buffer_size_range(device_info) {
        if config.buffer_size < min_buf || config.buffer_size > max_buf {
            return Err(ConfigError::UnsupportedBufferSize {
                requested: config.buffer_size,
                min_supported: min_buf,
                max_supported: max_buf,
            });
        }
    }

    // 4. Construir cpal::StreamConfig
    // Seleccionar la SupportedConfig que mejor coincida con la solicitud.
    // Criterio: cubre sample_rate y channels, prefiere f32.
    let _best: Option<&SupportedConfig> = device_info
        .supported_configs
        .iter()
        .filter(|c| {
            config.sample_rate >= c.min_sample_rate
                && config.sample_rate <= c.max_sample_rate
                && config.channels <= c.channels
        })
        .min_by_key(|c| if c.sample_format == "f32" { 0u8 } else { 1u8 });

    Ok(cpal::StreamConfig {
        channels: config.channels,
        sample_rate: SampleRate(config.sample_rate),
        buffer_size: cpal::BufferSize::Fixed(config.buffer_size),
    })
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;
    use crate::audio::device_manager::SupportedConfig;

    /// Crea un `AudioDeviceInfo` de prueba con una sola config f32.
    fn device(
        min_rate: u32,
        max_rate: u32,
        channels: u16,
        buf_range: Option<(u32, u32)>,
    ) -> AudioDeviceInfo {
        AudioDeviceInfo {
            id: "test-device".to_string(),
            name: "Test Device".to_string(),
            device_type: "input".to_string(),
            is_default: true,
            supported_configs: vec![SupportedConfig {
                channels,
                min_sample_rate: min_rate,
                max_sample_rate: max_rate,
                sample_format: "f32".to_string(),
                buffer_size_range: buf_range,
            }],
        }
    }

    fn config(sample_rate: u32, channels: u16, buffer_size: u32) -> AudioStreamConfig {
        AudioStreamConfig {
            device_id: "test-device".to_string(),
            sample_rate,
            channels,
            buffer_size,
        }
    }

    // --- Casos válidos ---

    #[test]
    fn valid_config_returns_ok() {
        let dev = device(44100, 48000, 2, None);
        let cfg = config(44100, 2, 512);
        assert!(validate_stream_config(&dev, &cfg).is_ok());
    }

    #[test]
    fn valid_config_returns_correct_cpal_config() {
        let dev = device(44100, 96000, 8, None);
        let cfg = config(48000, 4, 256);
        let result = validate_stream_config(&dev, &cfg).unwrap();
        assert_eq!(result.sample_rate.0, 48000);
        assert_eq!(result.channels, 4);
        assert_eq!(result.buffer_size, cpal::BufferSize::Fixed(256));
    }

    // --- Errores de sample rate ---

    #[test]
    fn unsupported_sample_rate_below_min() {
        let dev = device(44100, 96000, 2, None);
        let cfg = config(8000, 2, 512); // 8000 < 44100
        let err = validate_stream_config(&dev, &cfg).unwrap_err();
        assert!(matches!(err, ConfigError::UnsupportedSampleRate { .. }));
    }

    #[test]
    fn unsupported_sample_rate_above_max() {
        let dev = device(44100, 48000, 2, None);
        let cfg = config(96000, 2, 512); // 96000 > 48000
        match validate_stream_config(&dev, &cfg).unwrap_err() {
            ConfigError::UnsupportedSampleRate { requested, min_supported, max_supported } => {
                assert_eq!(requested, 96000);
                assert_eq!(min_supported, 44100);
                assert_eq!(max_supported, 48000);
            }
            other => panic!("Error inesperado: {:?}", other),
        }
    }

    #[test]
    fn sample_rate_at_boundary_is_valid() {
        let dev = device(44100, 96000, 2, None);
        assert!(validate_stream_config(&dev, &config(44100, 1, 512)).is_ok());
        assert!(validate_stream_config(&dev, &config(96000, 1, 512)).is_ok());
    }

    // --- Errores de canales ---

    #[test]
    fn too_many_channels_returns_error() {
        let dev = device(44100, 48000, 2, None);
        let cfg = config(44100, 8, 512); // device tiene 2, pedimos 8
        match validate_stream_config(&dev, &cfg).unwrap_err() {
            ConfigError::TooManyChannels { device_max, requested } => {
                assert_eq!(device_max, 2);
                assert_eq!(requested, 8);
            }
            other => panic!("Error inesperado: {:?}", other),
        }
    }

    #[test]
    fn channels_equal_to_max_is_valid() {
        let dev = device(44100, 48000, 8, None);
        assert!(validate_stream_config(&dev, &config(44100, 8, 512)).is_ok());
    }

    #[test]
    fn fewer_channels_than_device_is_valid() {
        let dev = device(44100, 48000, 8, None);
        assert!(validate_stream_config(&dev, &config(44100, 1, 512)).is_ok());
    }

    // --- Errores de buffer size ---

    #[test]
    fn buffer_size_below_min_returns_error() {
        let dev = device(44100, 48000, 2, Some((256, 4096)));
        let cfg = config(44100, 2, 64); // 64 < 256
        match validate_stream_config(&dev, &cfg).unwrap_err() {
            ConfigError::UnsupportedBufferSize { requested, min_supported, max_supported } => {
                assert_eq!(requested, 64);
                assert_eq!(min_supported, 256);
                assert_eq!(max_supported, 4096);
            }
            other => panic!("Error inesperado: {:?}", other),
        }
    }

    #[test]
    fn buffer_size_above_max_returns_error() {
        let dev = device(44100, 48000, 2, Some((64, 1024)));
        let cfg = config(44100, 2, 4096); // 4096 > 1024
        assert!(matches!(
            validate_stream_config(&dev, &cfg).unwrap_err(),
            ConfigError::UnsupportedBufferSize { .. }
        ));
    }

    #[test]
    fn buffer_size_ignored_when_range_unknown() {
        // Si el driver no informa rango, no se valida el buffer size
        let dev = device(44100, 48000, 2, None);
        // Cualquier buffer size debe pasar
        assert!(validate_stream_config(&dev, &config(44100, 2, 16)).is_ok());
        assert!(validate_stream_config(&dev, &config(44100, 2, 999_999)).is_ok());
    }

    // --- Dispositivo sin configs ---

    #[test]
    fn device_with_no_configs_returns_error() {
        let dev = AudioDeviceInfo {
            id: "empty".to_string(),
            name: "Empty".to_string(),
            device_type: "input".to_string(),
            is_default: false,
            supported_configs: vec![],
        };
        assert!(matches!(
            validate_stream_config(&dev, &config(44100, 1, 512)).unwrap_err(),
            ConfigError::NoSupportedConfigs
        ));
    }

    // --- Funciones de consulta para la UI ---

    #[test]
    fn supported_sample_rates_filters_correctly() {
        // Device soporta 44100–48000
        let dev = device(44100, 48000, 2, None);
        let rates = supported_sample_rates(&dev);
        assert!(rates.contains(&44100));
        assert!(rates.contains(&48000));
        assert!(!rates.contains(&96000)); // fuera de rango
        assert!(!rates.contains(&8000));  // fuera de rango
    }

    #[test]
    fn supported_sample_rates_empty_for_no_configs() {
        let dev = AudioDeviceInfo {
            id: "x".to_string(),
            name: "X".to_string(),
            device_type: "input".to_string(),
            is_default: false,
            supported_configs: vec![],
        };
        assert!(supported_sample_rates(&dev).is_empty());
    }

    #[test]
    fn max_channels_returns_highest() {
        let mut dev = device(44100, 48000, 2, None);
        dev.supported_configs.push(SupportedConfig {
            channels: 8,
            min_sample_rate: 44100,
            max_sample_rate: 48000,
            sample_format: "f32".to_string(),
            buffer_size_range: None,
        });
        assert_eq!(max_supported_channels(&dev), 8);
    }

    #[test]
    fn buffer_range_none_when_all_unknown() {
        let dev = device(44100, 48000, 2, None);
        assert!(supported_buffer_size_range(&dev).is_none());
    }

    #[test]
    fn buffer_range_union_of_all_ranges() {
        let mut dev = device(44100, 48000, 2, Some((256, 1024)));
        dev.supported_configs.push(SupportedConfig {
            channels: 2,
            min_sample_rate: 44100,
            max_sample_rate: 48000,
            sample_format: "i16".to_string(),
            buffer_size_range: Some((128, 2048)),
        });
        let range = supported_buffer_size_range(&dev).unwrap();
        assert_eq!(range, (128, 2048)); // min de 256,128 = 128; max de 1024,2048 = 2048
    }
}
