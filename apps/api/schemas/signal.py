from pydantic import BaseModel, ConfigDict, Field


class SignalInput(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    samples: list[float] = Field(..., min_length=1, description="Signal samples x[n]") # noqa: E501
    fs: float = Field(..., gt=0, description="Sample rate in Hz") # noqa: E501
    window_size: int = Field(default=4096, alias="windowSize")
    overlap: float = Field(default=0.75)
    window_type: str = Field(default="hann", alias="windowType")

class FrequencyResponseInput(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    x: list[float] = Field(..., min_length=1, description="Signal x[n]") # noqa: E501
    y: list[float] = Field(..., min_length=1, description="Signal y[n]") # noqa: E501
    fs: float = Field(..., gt=0, description="Sample rate in Hz") # noqa: E501
    window_size: int = Field(default=4096, alias="windowSize")
    overlap: float = Field(default=0.75)
    window_type: str = Field(default="hann", alias="windowType")

class ConvolutionInput(BaseModel):
    signal: list[float] = Field(..., min_length=1, description="Signal x[n]") # noqa: E501
    h: list[float] = Field(..., min_length=1, description="Impulse response h[n]") # noqa: E501

class FFTOutput(BaseModel):
    frequencies: list[float]
    magnitudes: list[float]

class FrequencyResponseOutput(BaseModel):
    frequencies: list[float]
    magnitude_db: list[float]
    phase_rad: list[float]

class ConvolutionOutput(BaseModel):
    samples: list[float]


class PureTonesInput(BaseModel):
    frequencies: list[float]
    amplitudes: list[float]
    fs: float
    duration: float


class AddNoiseInput(BaseModel):
    samples: list[float]
    fs: float
    snr_db: float


class ExportWavInput(BaseModel):
    samples: list[float]
    fs: float


class GeneratedSignalOutput(BaseModel):
    samples: list[float]
    fs: float
    duration: float


class GenerateSignalInput(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    signal_type: str = Field(..., alias="signalType", description="sine, square, triangle, white-noise, pink-noise, sweep")
    fs: float = Field(default=44100.0, gt=0)
    duration: float = Field(default=1.0, gt=0)
    amplitude: float = Field(default=1.0, ge=0)

    # Multi-tone / Pure tones parameter lists (optional)
    frequencies: list[float] = Field(default_factory=list)
    amplitudes: list[float] = Field(default_factory=list)

    # Single tone frequency
    frequency: float = Field(default=440.0, gt=0)

    # For sweeps
    f_start: float = Field(default=20.0, gt=0, alias="fStart")
    f_end: float = Field(default=20000.0, gt=0, alias="fEnd")
    sweep_type: str = Field(default="linear", alias="sweepType")

    # Optional noise addition
    apply_noise: bool = Field(default=False, alias="applyNoise")
    snr_db: float = Field(default=20.0, alias="snrDb")


