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
