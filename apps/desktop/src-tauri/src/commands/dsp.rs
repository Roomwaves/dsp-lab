use std::sync::Mutex;
use dsp_rs::{MovingAverageFilter, CombFilter, FIRFilter};
use dsp_rs::rustfft::{FftPlanner, num_complex::Complex};

/// State struct to manage active stateful filters in the desktop app.
pub struct DspState {
    pub moving_average: Option<(usize, MovingAverageFilter)>,
    pub comb: Option<((f32, f32, f32), CombFilter)>,
    pub fir: Option<(Vec<f32>, usize, FIRFilter)>, // (coefficients, block_size, filter)
}

impl DspState {
    pub fn new() -> Self {
        Self {
            moving_average: None,
            comb: None,
            fir: None,
        }
    }
}

impl Default for DspState {
    fn default() -> Self {
        Self::new()
    }
}

/// Processes a block of audio samples with the active filter.
#[tauri::command]
pub fn process_block_rt(
    samples: Vec<f32>,
    filter_type: String,
    params: serde_json::Value,
    state: tauri::State<'_, Mutex<DspState>>,
) -> Result<Vec<f32>, String> {
    let mut state_guard = state.lock().map_err(|_| "Failed to lock DspState".to_string())?;

    match filter_type.as_str() {
        "moving_average" => {
            let m = match params.get("M") {
                Some(v) => {
                    if let Some(u) = v.as_u64() {
                        u as usize
                    } else if let Some(f) = v.as_f64() {
                        f as usize
                    } else if let Some(s) = v.as_str() {
                        s.parse::<usize>().map_err(|e| e.to_string())?
                    } else {
                        return Err("Invalid M parameter format".to_string());
                    }
                }
                None => 8,
            };

            let filter = match &mut state_guard.moving_average {
                Some((current_m, filter)) if *current_m == m => filter,
                _ => {
                    let new_filter = MovingAverageFilter::new(m).map_err(|e| e.to_string())?;
                    state_guard.moving_average = Some((m, new_filter));
                    &mut state_guard.moving_average.as_mut().unwrap().1
                }
            };

            Ok(filter.process_block(&samples))
        }
        "comb" => {
            let b0 = params.get("b0").and_then(|v| v.as_f64().map(|f| f as f32)).unwrap_or(1.0);
            let b1 = params.get("b1").and_then(|v| v.as_f64().map(|f| f as f32)).unwrap_or(0.0);
            let b2 = params.get("b2").and_then(|v| v.as_f64().map(|f| f as f32)).unwrap_or(0.0);

            let filter = match &mut state_guard.comb {
                Some((coeffs, filter)) if *coeffs == (b0, b1, b2) => filter,
                _ => {
                    let new_filter = CombFilter::new(b0, b1, b2).map_err(|e| e.to_string())?;
                    state_guard.comb = Some(((b0, b1, b2), new_filter));
                    &mut state_guard.comb.as_mut().unwrap().1
                }
            };

            Ok(filter.process_block(&samples))
        }
        "fir" => {
            let coefficients_val = params.get("coefficients").ok_or_else(|| "Missing coefficients parameter".to_string())?;
            let coefficients_arr = coefficients_val.as_array().ok_or_else(|| "coefficients must be an array".to_string())?;
            let mut coefficients = Vec::with_capacity(coefficients_arr.len());
            for v in coefficients_arr {
                let val = v.as_f64().ok_or_else(|| "coefficient values must be numbers".to_string())? as f32;
                coefficients.push(val);
            }

            if coefficients.is_empty() {
                return Err("FIR coefficients cannot be empty".to_string());
            }

            let block_size = samples.len();
            let filter = match &mut state_guard.fir {
                Some((current_coeffs, current_block_size, filter)) if current_coeffs == &coefficients && *current_block_size == block_size => filter,
                _ => {
                    let new_filter = FIRFilter::new(&coefficients, block_size).map_err(|e| e.to_string())?;
                    state_guard.fir = Some((coefficients.clone(), block_size, new_filter));
                    &mut state_guard.fir.as_mut().unwrap().2
                }
            };

            Ok(filter.process_block(&samples))
        }
        _ => Err(format!("Unknown filter type: {}", filter_type)),
    }
}

/// Computes the FFT magnitude spectrum of a single audio block.
#[tauri::command]
pub fn compute_fft_rt(
    samples: Vec<f32>,
    fft_size: usize,
    window: String,
) -> Result<Vec<f32>, String> {
    if fft_size == 0 {
        return Err("fft_size must be greater than 0".to_string());
    }

    // Pad or truncate samples to fft_size
    let mut buffer = vec![0.0f32; fft_size];
    let copy_len = samples.len().min(fft_size);
    buffer[..copy_len].copy_from_slice(&samples[..copy_len]);

    // Generate window coefficients
    let mut win_coeffs = vec![1.0f32; fft_size];
    match window.as_str() {
        "hann" => {
            if fft_size > 1 {
                let mut sum = 0.0f32;
                for (n, val_ref) in win_coeffs.iter_mut().enumerate() {
                    let val = 0.5 * (1.0 - (2.0 * std::f32::consts::PI * n as f32 / (fft_size - 1) as f32).cos());
                    *val_ref = val;
                    sum += val;
                }
                if sum > 0.0 {
                    for val in win_coeffs.iter_mut() {
                        *val /= sum;
                    }
                }
            }
        }
        "hamming" => {
            if fft_size > 1 {
                let mut sum = 0.0f32;
                for (n, val_ref) in win_coeffs.iter_mut().enumerate() {
                    let val = 0.54 - 0.46 * (2.0 * std::f32::consts::PI * n as f32 / (fft_size - 1) as f32).cos();
                    *val_ref = val;
                    sum += val;
                }
                if sum > 0.0 {
                    for val in win_coeffs.iter_mut() {
                        *val /= sum;
                    }
                }
            }
        }
        "rectangular" => {
            // Equal to 1.0, normalize so sum = 1.0 (so divide by fft_size)
            let fft_size_f = fft_size as f32;
            for val in win_coeffs.iter_mut() {
                *val /= fft_size_f;
            }
        }
        _ => return Err(format!("Unsupported window type: {}", window)),
    }

    // Apply window to samples
    let mut complex_buffer: Vec<Complex<f32>> = buffer.iter()
        .zip(win_coeffs.iter())
        .map(|(&x, &w)| Complex::new(x * w, 0.0))
        .collect();

    // Compute FFT
    let mut planner = FftPlanner::new();
    let fft = planner.plan_fft_forward(fft_size);
    fft.process(&mut complex_buffer);

    // Calculate magnitudes of positive half
    let half_size = fft_size / 2;
    let magnitudes: Vec<f32> = complex_buffer.iter()
        .take(half_size)
        .map(|c| c.norm())
        .collect();

    Ok(magnitudes)
}
