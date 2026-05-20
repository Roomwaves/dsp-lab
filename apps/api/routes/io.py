import os
import tempfile

import numpy as np
from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel
from scipy.io import wavfile

from ..schemas.signal import SignalInput


class UploadResponse(BaseModel):
    samples: list[float]
    fs: float
    duration_s: float
    channels: int

router = APIRouter(prefix="/io", tags=["IO"])

@router.post("/upload", response_model=UploadResponse)
async def upload_audio(file: UploadFile = File(...)) -> UploadResponse:
    if not file.filename.endswith(".wav"):
        raise HTTPException(status_code=400, detail="Only .wav files are supported")
    
    # Save temporarily
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        try:
            fs, data = wavfile.read(tmp_path)
            
            # Handle mono/stereo
            if len(data.shape) > 1:
                channels = data.shape[1]
                # Convert to mono by averaging channels
                samples = data.mean(axis=1)
            else:
                channels = 1
                samples = data
                
            # Normalize to float if it's not
            if samples.dtype != np.float32 and samples.dtype != np.float64:
                # Basic normalization for 16-bit PCM
                if samples.dtype == np.int16:
                    samples = samples.astype(np.float32) / 32768.0
                elif samples.dtype == np.int32:
                    samples = samples.astype(np.float32) / 2147483648.0
                else:
                    samples = samples.astype(np.float32)
                    
            duration_s = len(samples) / fs
            
            return UploadResponse(
                samples=samples.tolist(),
                fs=float(fs),
                duration_s=float(duration_s),
                channels=channels
            )
        finally:
            os.remove(tmp_path)
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail=f"Error processing audio file: {str(e)}"
        )

@router.post("/download", response_class=FileResponse)
def download_audio(body: SignalInput, background_tasks: BackgroundTasks):
    try:
        # Create a temporary file that won't be deleted when closed
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        tmp.close()
        
        signal = np.array(body.samples, dtype=np.float32)
        
        # Ensure it's in a valid range [-1.0, 1.0] to save as wav
        # but scipy wavfile can write float32 directly.
        wavfile.write(tmp.name, int(body.fs), signal)
        
        background_tasks.add_task(os.remove, tmp.name)
        
        return FileResponse(
            path=tmp.name,
            filename="signal.wav",
            media_type="audio/wav",
            background=background_tasks
        )
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))
