use dsp_rs::{MovingAverageFilter, CombFilter, FIRFilter, StreamingFFT};
use approx::assert_relative_eq;
use std::fs::File;
use std::io::Read;
use std::path::Path;

fn load_f32_fixture<P: AsRef<Path>>(path: P) -> Vec<f32> {
    let mut file = File::open(path).expect("failed to open fixture");
    let mut bytes = Vec::new();
    file.read_to_end(&mut bytes).expect("failed to read fixture");

    assert_eq!(&bytes[0..6], b"\x93NUMPY");
    let major = bytes[6];

    let header_len = if major == 1 {
        let mut len_bytes = [0u8; 2];
        len_bytes.copy_from_slice(&bytes[8..10]);
        u16::from_le_bytes(len_bytes) as usize
    } else {
        let mut len_bytes = [0u8; 4];
        len_bytes.copy_from_slice(&bytes[8..12]);
        u32::from_le_bytes(len_bytes) as usize
    };

    let header_start = if major == 1 { 10 } else { 12 };
    let data_start = header_start + header_len;

    let data_bytes = &bytes[data_start..];
    let mut result = Vec::with_capacity(data_bytes.len() / 4);
    for chunk in data_bytes.chunks_exact(4) {
        let mut float_bytes = [0u8; 4];
        float_bytes.copy_from_slice(chunk);
        result.push(f32::from_le_bytes(float_bytes));
    }
    result
}

#[test]
fn test_matches_python_fixture() {
    let input = load_f32_fixture("tests/fixtures/input.npy");
    let expected = load_f32_fixture("tests/fixtures/moving_average_M8.npy");

    let mut filter = MovingAverageFilter::new(8).unwrap();
    let output = filter.process_block(&input);

    assert_eq!(output.len(), expected.len());
    for (a, b) in output.iter().zip(expected.iter()) {
        assert_relative_eq!(a, b, epsilon = 1e-5);
    }
}

#[test]
fn test_comb_matches_python_fixture() {
    let input = load_f32_fixture("tests/fixtures/input.npy");
    let expected = load_f32_fixture("tests/fixtures/comb_output.npy");

    let mut filter = CombFilter::new(0.5, 0.2, 0.1).unwrap();
    let output = filter.process_block(&input);

    assert_eq!(output.len(), expected.len());
    for (a, b) in output.iter().zip(expected.iter()) {
        assert_relative_eq!(a, b, epsilon = 1e-5);
    }
}

#[test]
fn test_fir_matches_python_fixture() {
    let input = load_f32_fixture("tests/fixtures/input.npy");
    let h = load_f32_fixture("tests/fixtures/fir_coeffs.npy");
    let expected = load_f32_fixture("tests/fixtures/fir_output.npy");

    let block_size = 20;
    let mut filter = FIRFilter::new(&h, block_size).unwrap();

    let mut output = Vec::new();
    for chunk in input.chunks_exact(block_size) {
        let block_out = filter.process_block(chunk);
        output.extend(block_out);
    }

    assert_eq!(output.len(), expected.len());
    for (a, b) in output.iter().zip(expected.iter()) {
        assert_relative_eq!(a, b, epsilon = 1e-5);
    }
}

#[test]
fn test_streaming_fft() {
    let fft_size = 64;
    let hop_size = 16;
    let mut streaming_fft = StreamingFFT::new(fft_size, hop_size);

    let input = vec![0.5f32; 100];

    // Ingest first 63 samples -> should not produce FFT yet
    let res = streaming_fft.process(&input[0..63]);
    assert!(res.is_none());

    // Ingest 64th sample -> should produce FFT of size 32
    let res = streaming_fft.process(&input[63..64]);
    assert!(res.is_some());
    let mags = res.unwrap();
    assert_eq!(mags.len(), fft_size / 2);
    assert!(mags[0] > 0.0);

    // Ingest next 16 samples -> should produce another FFT (due to hop_size = 16)
    let res = streaming_fft.process(&input[64..80]);
    assert!(res.is_some());
    let mags = res.unwrap();
    assert_eq!(mags.len(), fft_size / 2);
}
