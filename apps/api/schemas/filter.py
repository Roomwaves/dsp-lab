from typing import Any, Literal

from pydantic import BaseModel, Field


class MovingAverageParams(BaseModel):
    samples: list[float] = Field(..., min_length=1, description="Signal samples x[n]") # noqa: E501
    M: int = Field(..., gt=0, description="Window size M") # noqa: E501
    passes: int = Field(default=1, ge=1, le=3, description="Number of passes (1, 2, or 3)") # noqa: E501

class CombFilterParams(BaseModel):
    samples: list[float] = Field(..., min_length=1, description="Signal samples x[n]") # noqa: E501
    b0: float = Field(..., description="Coefficient b0") # noqa: E501
    b1: float = Field(..., description="Coefficient b1") # noqa: E501
    b2: float = Field(..., description="Coefficient b2") # noqa: E501

class FIRParams(BaseModel):
    samples: list[float] = Field(..., min_length=1, description="Signal samples x[n]") # noqa: E501
    coefficients: list[float] = Field(..., min_length=1, description="FIR filter coefficients") # noqa: E501

class FIRTruncateParams(BaseModel):
    coefficients: list[float] = Field(..., min_length=1, description="Original FIR filter coefficients") # noqa: E501
    N: int = Field(..., gt=0, description="Number of coefficients to keep") # noqa: E501

class FilterOutput(BaseModel):
    samples: list[float]

class ImpulseResponseParams(BaseModel):
    filter_type: Literal["moving_average", "comb", "fir"]
    params: dict[str, Any] = Field(..., description="Parameters for the specific filter") # noqa: E501
    N: int = Field(default=100, gt=0, description="Length of the impulse response to generate") # noqa: E501

class MovingAverageResponseParams(BaseModel):
    M: int = Field(..., gt=0, description="Window size M")
    passes: int = Field(default=1, ge=1, le=3, description="Number of passes")
    fs: float = Field(default=44100.0, gt=0, description="Sample rate in Hz")

class CombResponseParams(BaseModel):
    b0: float = Field(default=1.0)
    b1: float = Field(default=0.0)
    b2: float = Field(default=0.25)
    fs: float = Field(default=44100.0, gt=0, description="Sample rate in Hz")

class FIRResponseParams(BaseModel):
    coefficients: list[float] = Field(default_factory=list, description="FIR filter coefficients")
    fs: float = Field(default=44100.0, gt=0, description="Sample rate in Hz")

