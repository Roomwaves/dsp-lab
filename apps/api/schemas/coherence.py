from pydantic import BaseModel, ConfigDict, Field


class CoherenceInput(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    x: list[float] = Field(..., min_length=1, description="Signal x[n]") # noqa: E501
    y: list[float] = Field(..., min_length=1, description="Signal y[n]") # noqa: E501
    fs: float = Field(..., gt=0, description="Sample rate in Hz") # noqa: E501
    n_segments: int = Field(default=8, gt=0, alias="averages", description="Number of segments for Welch's method") # noqa: E501
    window_size: int = Field(default=4096, alias="windowSize")
    overlap: float = Field(default=0.75)
    window_type: str = Field(default="hann", alias="windowType")

class PSDInput(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    signal: list[float] = Field(..., min_length=1, description="Signal samples") # noqa: E501
    fs: float = Field(..., gt=0, description="Sample rate in Hz") # noqa: E501
    n_segments: int = Field(default=8, gt=0, alias="averages", description="Number of segments for Welch's method") # noqa: E501

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
