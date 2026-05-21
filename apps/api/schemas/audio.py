from typing import Optional

from pydantic import BaseModel, Field


class AudioDeviceInfo(BaseModel):
    id: int
    name: str
    max_input_channels: int
    max_output_channels: int
    default_samplerate: float

class AudioStreamConfig(BaseModel):
    device_id: Optional[int] = Field(None, description="Device ID to use, defaults to system default") # noqa: E501
    channels: int = Field(default=1, gt=0, description="Number of audio channels") # noqa: E501
    samplerate: float = Field(default=44100.0, gt=0, description="Sample rate in Hz") # noqa: E501
    chunk_size: int = Field(default=1024, gt=0, description="Chunk size for the audio stream") # noqa: E501
