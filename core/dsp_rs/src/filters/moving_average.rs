use crate::error::DspError;

/// Causal Moving Average Filter.
///
/// For each sample, computes the average of the last `M` samples.
/// The state persists across blocks.
pub struct MovingAverageFilter {
    m: usize,
    buffer: Vec<f32>,
    write_index: usize,
}

impl MovingAverageFilter {
    /// Creates a new `MovingAverageFilter` with window size `m`.
    pub fn new(m: usize) -> Result<Self, DspError> {
        if m == 0 {
            return Err(DspError::InvalidParameter("M must be >= 1".into()));
        }
        Ok(Self {
            m,
            buffer: vec![0.0; m],
            write_index: 0,
        })
    }

    /// Processes a block of audio samples.
    /// Output length matches input length.
    pub fn process_block(&mut self, input: &[f32]) -> Vec<f32> {
        let mut output = Vec::with_capacity(input.len());
        for &x in input {
            self.buffer[self.write_index] = x;
            self.write_index = (self.write_index + 1) % self.m;
            let sum: f32 = self.buffer.iter().sum();
            output.push(sum / self.m as f32);
        }
        output
    }

    /// Resets the filter state.
    pub fn reset(&mut self) {
        self.buffer.fill(0.0);
        self.write_index = 0;
    }
}
