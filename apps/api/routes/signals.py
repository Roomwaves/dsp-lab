import os
import tempfile

import numpy as np
from core.dsp.signals import (
    add_white_noise,
    generate_pink_noise,
    generate_pure_tones,
    generate_square_wave,
    generate_sweep,
    generate_triangle_wave,
    generate_white_noise,
)
from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from scipy.io import wavfile

from ..schemas.signal import (
    AddNoiseInput,
    ExportWavInput,
    GeneratedSignalOutput,
    GenerateSignalInput,
    PureTonesInput,
)

router = APIRouter(prefix="/signals", tags=["Signals"])


@router.post("/pure-tones", response_model=GeneratedSignalOutput)
def generate_tones_endpoint(body: PureTonesInput) -> GeneratedSignalOutput:
    try:
        samples = generate_pure_tones(
            frequencies=body.frequencies,
            amplitudes=body.amplitudes,
            fs=body.fs,
            duration=body.duration,
        )
        return GeneratedSignalOutput(
            samples=samples.tolist(), fs=body.fs, duration=body.duration
        )
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/add-noise", response_model=GeneratedSignalOutput)
def add_noise_endpoint(body: AddNoiseInput) -> GeneratedSignalOutput:
    try:
        signal = np.array(body.samples)
        noisy_signal = add_white_noise(signal, body.snr_db)
        duration = len(body.samples) / body.fs
        return GeneratedSignalOutput(
            samples=noisy_signal.tolist(), fs=body.fs, duration=duration
        )
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/export-wav", response_class=FileResponse)
def export_wav_endpoint(
    body: ExportWavInput, background_tasks: BackgroundTasks
) -> FileResponse:
    try:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        tmp.close()

        signal = np.array(body.samples, dtype=np.float32)
        wavfile.write(tmp.name, int(body.fs), signal)

        background_tasks.add_task(os.remove, tmp.name)

        return FileResponse(
            path=tmp.name,
            filename="signal.wav",
            media_type="audio/wav",
            background=background_tasks,
        )
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/generate", response_model=GeneratedSignalOutput)
def generate_signal_endpoint(body: GenerateSignalInput) -> GeneratedSignalOutput:
    try:
        sig_type = body.signal_type.lower()
        if sig_type == "sine":
            if body.frequencies and body.amplitudes:
                samples = generate_pure_tones(
                    frequencies=body.frequencies,
                    amplitudes=body.amplitudes,
                    fs=body.fs,
                    duration=body.duration,
                )
            else:
                samples = generate_pure_tones(
                    frequencies=[body.frequency],
                    amplitudes=[body.amplitude],
                    fs=body.fs,
                    duration=body.duration,
                )
        elif sig_type == "square":
            samples = generate_square_wave(
                frequency=body.frequency,
                amplitude=body.amplitude,
                fs=body.fs,
                duration=body.duration,
            )
        elif sig_type == "triangle":
            samples = generate_triangle_wave(
                frequency=body.frequency,
                amplitude=body.amplitude,
                fs=body.fs,
                duration=body.duration,
            )
        elif sig_type == "white-noise":
            samples = generate_white_noise(
                amplitude=body.amplitude,
                fs=body.fs,
                duration=body.duration,
                gaussian=False,
            )
        elif sig_type == "pink-noise":
            samples = generate_pink_noise(
                amplitude=body.amplitude, fs=body.fs, duration=body.duration
            )
        elif sig_type == "sweep":
            samples = generate_sweep(
                f_start=body.f_start,
                f_end=body.f_end,
                sweep_type=body.sweep_type,
                amplitude=body.amplitude,
                fs=body.fs,
                duration=body.duration,
            )
        else:
            raise HTTPException(
                status_code=400, detail=f"Unsupported signal type: {body.signal_type}"
            )

        if body.apply_noise:
            samples = add_white_noise(samples, body.snr_db)

        return GeneratedSignalOutput(
            samples=samples.tolist(), fs=body.fs, duration=body.duration
        )
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))
