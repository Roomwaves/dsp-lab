use std::collections::VecDeque;
use std::sync::Arc;
use rustfft::{Fft, FftPlanner, num_complex::Complex};

/// Sliding window FFT analyzer.
///
/// Ingests samples into a ring buffer, applies a Hann window,
/// computes the FFT, and calculates magnitude spectrum.
/// Supports exponential averaging.
pub struct StreamingFFT {
    fft_size: usize,
    hop_size: usize,
    window: Vec<f32>,
    ring_buffer: VecDeque<f32>,
    #[allow(dead_code)]
    planner: FftPlanner<f32>,
    fft: Arc<dyn Fft<f32>>,
    averaging_alpha: Option<f32>,
    prev_magnitudes: Vec<f32>,
    fft_buffer: Vec<Complex<f32>>,
}

impl StreamingFFT {
    /// Creates a new `StreamingFFT` with `fft_size` and `hop_size`.
    pub fn new(fft_size: usize, hop_size: usize) -> Self {
        assert!(fft_size > 0, "FFT size must be greater than 0");
        assert!(hop_size > 0, "Hop size must be greater than 0");

        let mut planner = FftPlanner::new();
        let fft = planner.plan_fft_forward(fft_size);

        // Precompute Hann window and normalize it (coherent gain normalization)
        let mut window = vec![0.0; fft_size];
        if fft_size == 1 {
            window[0] = 1.0;
        } else {
            let mut sum = 0.0;
            for (n, val_ref) in window.iter_mut().enumerate() {
                let val = 0.5 * (1.0 - (2.0 * std::f32::consts::PI * n as f32 / (fft_size - 1) as f32).cos());
                *val_ref = val;
                sum += val;
            }
            if sum > 0.0 {
                for val in window.iter_mut() {
                    *val /= sum;
                }
            }
        }

        Self {
            fft_size,
            hop_size,
            window,
            ring_buffer: VecDeque::with_capacity(fft_size * 2),
            planner,
            fft,
            averaging_alpha: None,
            prev_magnitudes: vec![],
            fft_buffer: vec![Complex::new(0.0, 0.0); fft_size],
        }
    }

    /// Ingests new samples. When enough samples are available,
    /// computes the FFT, applies windowing and averaging, and returns magnitudes.
    pub fn process(&mut self, samples: &[f32]) -> Option<Vec<f32>> {
        self.ring_buffer.extend(samples);

        if self.ring_buffer.len() < self.fft_size {
            return None;
        }

        // Copy first fft_size samples to FFT buffer and apply window
        for i in 0..self.fft_size {
            let sample = self.ring_buffer[i];
            self.fft_buffer[i] = Complex::new(sample * self.window[i], 0.0);
        }

        // Forward FFT
        self.fft.process(&mut self.fft_buffer);

        // Get positive half magnitudes
        let half_size = self.fft_size / 2;
        let mut magnitudes = Vec::with_capacity(half_size);
        for i in 0..half_size {
            magnitudes.push(self.fft_buffer[i].norm());
        }

        // Exponential averaging
        if let Some(alpha) = self.averaging_alpha {
            if self.prev_magnitudes.is_empty() {
                self.prev_magnitudes = magnitudes.clone();
            } else {
                for (prev_mag, &mag) in self.prev_magnitudes.iter_mut().zip(magnitudes.iter()) {
                    *prev_mag = alpha * *prev_mag + (1.0 - alpha) * mag;
                }
            }
            magnitudes = self.prev_magnitudes.clone();
        }

        // Advance the ring buffer by hop_size
        self.ring_buffer.drain(0..self.hop_size);

        Some(magnitudes)
    }

    /// Sets the exponential averaging factor `alpha` (usually in range [0, 1)).
    pub fn with_averaging(mut self, alpha: f32) -> Self {
        self.averaging_alpha = Some(alpha);
        self
    }
}
