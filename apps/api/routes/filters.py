import numpy as np
from core.dsp.filters import apply_fir, comb_filter, moving_average, truncate_fir
from fastapi import APIRouter, HTTPException

from ..schemas.filter import (
    CombFilterParams,
    FilterOutput,
    FIRParams,
    FIRTruncateParams,
    ImpulseResponseParams,
    MovingAverageParams,
)

router = APIRouter(prefix="/filters", tags=["Filters"])

@router.post("/moving-average", response_model=FilterOutput)
def apply_moving_average(body: MovingAverageParams) -> FilterOutput:
    try:
        signal = np.array(body.samples)
        result = moving_average(signal, M=body.M, passes=body.passes)
        return FilterOutput(samples=result.tolist())
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

@router.post("/comb", response_model=FilterOutput)
def apply_comb_filter(body: CombFilterParams) -> FilterOutput:
    try:
        signal = np.array(body.samples)
        result = comb_filter(signal, b0=body.b0, b1=body.b1, b2=body.b2)
        return FilterOutput(samples=result.tolist())
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

@router.post("/fir/apply", response_model=FilterOutput)
def apply_fir_filter(body: FIRParams) -> FilterOutput:
    try:
        signal = np.array(body.samples)
        coeffs = np.array(body.coefficients)
        result = apply_fir(signal, coeffs)
        return FilterOutput(samples=result.tolist())
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

@router.post("/fir/truncate", response_model=FilterOutput)
def truncate_fir_filter(body: FIRTruncateParams) -> FilterOutput:
    try:
        coeffs = np.array(body.coefficients)
        result = truncate_fir(coeffs, N=body.N)
        return FilterOutput(samples=result.tolist())
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

@router.post("/impulse-response", response_model=FilterOutput)
def compute_impulse_response(body: ImpulseResponseParams) -> FilterOutput:
    try:
        # Generate impulse: delta[n]
        delta = np.zeros(body.N)
        delta[0] = 1.0

        if body.filter_type == "moving_average":
            M = int(body.params.get("M", 1))
            passes = int(body.params.get("passes", 1))
            result = moving_average(delta, M=M, passes=passes)
        elif body.filter_type == "comb":
            b0 = float(body.params.get("b0", 1.0))
            b1 = float(body.params.get("b1", 0.0))
            b2 = float(body.params.get("b2", 0.0))
            result = comb_filter(delta, b0=b0, b1=b1, b2=b2)
        elif body.filter_type == "fir":
            coeffs = np.array(body.params.get("coefficients", [1.0]))
            result = apply_fir(delta, coeffs)
        else:
            raise ValueError(f"Unknown filter type: {body.filter_type}")

        return FilterOutput(samples=result.tolist())
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))
