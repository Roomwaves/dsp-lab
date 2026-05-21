use crate::error::DspError;

/// Causal Feedforward Comb Filter.
///
/// Implements y[n] = b0 * x[n] + b1 * x[n-1] + b2 * x[n-2].
/// State (delay buffer) persists across blocks.
pub struct CombFilter {
    b0: f32,
    b1: f32,
    b2: f32,
    delay_buffer: [f32; 2],
}

impl CombFilter {
    /// Creates a new `CombFilter` with coefficients `b0`, `b1`, and `b2`.
    pub fn new(b0: f32, b1: f32, b2: f32) -> Result<Self, DspError> {
        Ok(Self {
            b0,
            b1,
            b2,
            delay_buffer: [0.0; 2],
        })
    }

    /// Processes a block of audio samples.
    pub fn process_block(&mut self, input: &[f32]) -> Vec<f32> {
        let mut output = Vec::with_capacity(input.len());
        for &x in input {
            let y = self.b0 * x + self.b1 * self.delay_buffer[0] + self.b2 * self.delay_buffer[1];
            output.push(y);
            self.delay_buffer[1] = self.delay_buffer[0];
            self.delay_buffer[0] = x;
        }
        output
    }

    /// Resets the filter state.
    pub fn reset(&mut self) {
        self.delay_buffer = [0.0; 2];
    }
}
