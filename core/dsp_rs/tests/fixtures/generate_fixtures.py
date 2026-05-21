import numpy as np
import os
import scipy.signal

def main():
    dir_path = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(dir_path, exist_ok=True)
    
    # 1. Input signal (100 samples)
    rng = np.random.default_rng(42)
    input_signal = rng.standard_normal(100).astype(np.float32)
    np.save(os.path.join(dir_path, "input.npy"), input_signal)
    
    # 2. Moving average M=8
    b_ma = np.ones(8, dtype=np.float32) / 8.0
    ma_output = scipy.signal.lfilter(b_ma, 1.0, input_signal).astype(np.float32)
    np.save(os.path.join(dir_path, "moving_average_M8.npy"), ma_output)
    
    # 3. Comb filter: b0=0.5, b1=0.2, b2=0.1
    b_comb = np.array([0.5, 0.2, 0.1], dtype=np.float32)
    comb_output = scipy.signal.lfilter(b_comb, 1.0, input_signal).astype(np.float32)
    np.save(os.path.join(dir_path, "comb_output.npy"), comb_output)
    
    # 4. FIR filter: coefficients
    h_fir = np.array([0.1, -0.2, 0.3, 0.4, -0.1, 0.05], dtype=np.float32)
    fir_output = scipy.signal.lfilter(h_fir, 1.0, input_signal).astype(np.float32)
    np.save(os.path.join(dir_path, "fir_coeffs.npy"), h_fir)
    np.save(os.path.join(dir_path, "fir_output.npy"), fir_output)
    
    print("Fixtures generated successfully!")

if __name__ == "__main__":
    main()
