use std::sync::Arc;
use rustfft::{Fft, FftPlanner, num_complex::Complex};
use crate::error::DspError;

/// FIR Filter using the Overlap-Save method.
///
/// Computes linear convolution block-by-block using FFT.
/// State (overlap buffer of size `len(h) - 1`) persists across blocks.
pub struct FIRFilter {
    block_size: usize,
    m: usize,
    fft_size: usize,
    overlap_buffer: Vec<f32>,
    h_fft: Vec<Complex<f32>>,
    fft: Arc<dyn Fft<f32>>,
    ifft: Arc<dyn Fft<f32>>,
    x_block: Vec<Complex<f32>>,
}

impl FIRFilter {
    /// Creates a new `FIRFilter` with coefficients `h` and expected `block_size`.
    pub fn new(h: &[f32], block_size: usize) -> Result<Self, DspError> {
        if h.is_empty() {
            return Err(DspError::InvalidParameter("Impulse response coefficients cannot be empty".into()));
        }
        if block_size == 0 {
            return Err(DspError::InvalidParameter("Block size must be >= 1".into()));
        }

        let m = h.len();
        let fft_size = block_size + m - 1;

        let mut planner = FftPlanner::new();
        let fft = planner.plan_fft_forward(fft_size);
        let ifft = planner.plan_fft_inverse(fft_size);

        // Precompute FFT of padded impulse response
        let mut h_padded = vec![Complex::new(0.0, 0.0); fft_size];
        for i in 0..m {
            h_padded[i] = Complex::new(h[i], 0.0);
        }
        fft.process(&mut h_padded);

        Ok(Self {
            block_size,
            m,
            fft_size,
            overlap_buffer: vec![0.0; m - 1],
            h_fft: h_padded,
            fft,
            ifft,
            x_block: vec![Complex::new(0.0, 0.0); fft_size],
        })
    }

    /// Processes a block of samples using overlap-save.
    ///
    /// # Panics
    /// Panics if `input.len()` does not equal the configured `block_size`.
    pub fn process_block(&mut self, input: &[f32]) -> Vec<f32> {
        assert_eq!(
            input.len(),
            self.block_size,
            "Input block size {} must match configured block size {}",
            input.len(),
            self.block_size
        );

        let m_minus_1 = self.m - 1;

        // Construct x_block = [overlap_buffer, input]
        for i in 0..m_minus_1 {
            self.x_block[i] = Complex::new(self.overlap_buffer[i], 0.0);
        }
        for i in 0..self.block_size {
            self.x_block[m_minus_1 + i] = Complex::new(input[i], 0.0);
        }

        // Forward FFT
        self.fft.process(&mut self.x_block);

        // Pointwise complex multiplication
        for i in 0..self.fft_size {
            self.x_block[i] *= self.h_fft[i];
        }

        // Inverse FFT
        self.ifft.process(&mut self.x_block);

        // Extract output: starting at index m - 1, length block_size
        // Normalize because rustfft's IFFT is unnormalized
        let mut output = vec![0.0; self.block_size];
        let fft_size_f = self.fft_size as f32;
        for i in 0..self.block_size {
            output[i] = self.x_block[m_minus_1 + i].re / fft_size_f;
        }

        // Update overlap buffer
        if m_minus_1 > 0 {
            self.overlap_buffer.copy_from_slice(&input[self.block_size - m_minus_1..]);
        }

        output
    }

    /// Resets the filter state.
    pub fn reset(&mut self) {
        self.overlap_buffer.fill(0.0);
        self.x_block.fill(Complex::new(0.0, 0.0));
    }
}
