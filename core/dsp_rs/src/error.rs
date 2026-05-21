#[derive(Debug, thiserror::Error)]
pub enum DspError {
    #[error("Invalid parameter: {0}")]
    InvalidParameter(String),

    #[error("Buffer too small: expected >= {expected}, got {actual}")]
    BufferTooSmall { expected: usize, actual: usize },

    #[error("IO error loading fixture: {0}")]
    FixtureLoadError(String),
}
