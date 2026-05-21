pub mod error;
pub mod filters;
pub mod analysis;

pub use error::DspError;
pub use filters::{MovingAverageFilter, CombFilter, FIRFilter};
pub use analysis::StreamingFFT;