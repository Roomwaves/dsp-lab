import numpy as np
from core.dsp.coherence import compute_coherence, compute_cpsd, compute_psd
from fastapi import APIRouter, HTTPException

from ..schemas.coherence import (
    CoherenceInput,
    CoherenceOutput,
    CPSDOutput,
    PSDInput,
    PSDOutput,
)

router = APIRouter(prefix="/coherence", tags=["Coherence"])

@router.post("/psd", response_model=PSDOutput)
def psd_endpoint(body: PSDInput) -> PSDOutput:
    try:
        signal = np.array(body.signal)
        freqs, gxx = compute_psd(signal, body.fs, n_segments=body.n_segments)
        return PSDOutput(
            frequencies=freqs.tolist(),
            psd=gxx.tolist()
        )
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

@router.post("/cpsd", response_model=CPSDOutput)
def cpsd_endpoint(body: CoherenceInput) -> CPSDOutput:
    try:
        x = np.array(body.x)
        y = np.array(body.y)
        freqs, gxy = compute_cpsd(x, y, body.fs, n_segments=body.n_segments)
        return CPSDOutput(
            frequencies=freqs.tolist(),
            cpsd_real=gxy.real.tolist(),
            cpsd_imag=gxy.imag.tolist()
        )
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

@router.post("/compute", response_model=CoherenceOutput)
def coherence_endpoint(body: CoherenceInput) -> CoherenceOutput:
    try:
        x = np.array(body.x)
        y = np.array(body.y)
        freqs, coherence = compute_coherence(
            x, y, body.fs,
            n_segments=body.n_segments,
            window_size=body.window_size,
            overlap=body.overlap,
            window_type=body.window_type
        )
        return CoherenceOutput(
            frequencies=freqs.tolist(),
            coherence=coherence.tolist()
        )
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))
