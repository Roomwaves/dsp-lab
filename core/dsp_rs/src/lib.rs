pub fn convolve(signal: &[f64], kernel: &[f64]) -> Vec<f64> {
    todo!("implement convolution")
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    #[should_panic(expected = "implement convolution")]
    fn test_convolve_placeholder() {
        convolve(&[1.0], &[1.0]);
    }
}