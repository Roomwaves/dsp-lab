from pydantic import BaseModel, Field


class CoherenceInput(BaseModel):
    x: list[float] = Field(..., min_length=1, description="Signal x[n]") # noqa: E501
    y: list[float] = Field(..., min_length=1, description="Signal y[n]") # noqa: E501
    fs: float = Field(..., gt=0, description="Sample rate in Hz") # noqa: E501
    n_segments: int = Field(default=8, gt=0, description="Number of segments for Welch's method") # noqa: E501

class PSDInput(BaseModel):
    signal: list[float] = Field(..., min_length=1, description="Signal samples") # noqa: E501
    fs: float = Field(..., gt=0, description="Sample rate in Hz") # noqa: E501
    n_segments: int = Field(default=8, gt=0, description="Number of segments for Welch's method") # noqa: E501

class PSDOutput(BaseModel):
    frequencies: list[float]
    psd: list[float]

class CPSDOutput(BaseModel):
    frequencies: list[float]
    cpsd_real: list[float]
    cpsd_imag: list[float]

class CoherenceOutput(BaseModel):
    frequencies: list[float]
    coherence: list[float]
