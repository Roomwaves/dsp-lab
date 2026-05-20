from pydantic import BaseModel, Field


class SignalInput(BaseModel):
    samples: list[float] = Field(..., min_length=1, description="Signal samples x[n]") # noqa: E501
    fs: float = Field(..., gt=0, description="Sample rate in Hz") # noqa: E501

class FFTOutput(BaseModel):
    frequencies: list[float]
    magnitudes: list[float]

class FrequencyResponseOutput(BaseModel):
    frequencies: list[float]
    magnitude_db: list[float]
    phase_rad: list[float]

class ConvolutionOutput(BaseModel):
    samples: list[float]
