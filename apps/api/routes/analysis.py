import numpy as np
from core.dsp.analysis import (
    compute_fft,
    compute_frequency_response,
    compute_magnitude_db,
    compute_phase,
    convolve_frequency,
    convolve_time,
)
from fastapi import APIRouter, HTTPException

from ..schemas.signal import (
    ConvolutionInput,
    ConvolutionOutput,
    FFTOutput,
    FrequencyResponseInput,
    FrequencyResponseOutput,
    SignalInput,
)

router = APIRouter(prefix="/analysis", tags=["Analysis"])

@router.post("/fft", response_model=FFTOutput)
def fft_endpoint(body: SignalInput) -> FFTOutput:
    try:
        signal = np.array(body.samples)
        freqs, mags = compute_fft(signal, body.fs)
        return FFTOutput(
            frequencies=freqs.tolist(),
            magnitudes=mags.tolist()
        )
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

@router.post("/frequency-response", response_model=FrequencyResponseOutput)
def frequency_response_endpoint(
    body: FrequencyResponseInput
) -> FrequencyResponseOutput:
    try:
        x = np.array(body.x)
        y = np.array(body.y)
        freqs, h_complex = compute_frequency_response(x, y, body.fs)
        
        mag_db = compute_magnitude_db(h_complex)
        phase_rad = compute_phase(h_complex)
        
        return FrequencyResponseOutput(
            frequencies=freqs.tolist(),
            magnitude_db=mag_db.tolist(),
            phase_rad=phase_rad.tolist()
        )
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

@router.post("/convolve/time", response_model=ConvolutionOutput)
def convolve_time_endpoint(body: ConvolutionInput) -> ConvolutionOutput:
    try:
        signal = np.array(body.signal)
        h = np.array(body.h)
        result = convolve_time(signal, h)
        return ConvolutionOutput(samples=result.tolist())
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

@router.post("/convolve/frequency", response_model=ConvolutionOutput)
def convolve_frequency_endpoint(body: ConvolutionInput) -> ConvolutionOutput:
    try:
        signal = np.array(body.signal)
        h = np.array(body.h)
        result = convolve_frequency(signal, h)
        return ConvolutionOutput(samples=result.tolist())
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))
