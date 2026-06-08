import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import analysis, coherence, filters, signals
from .routes import io as io_routes

ALLOWED_ORIGINS = [
    "http://localhost:1420",  # Tauri dev
    "tauri://localhost",      # Tauri production
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup logic (future: warm up models, open audio devices)
    yield
    # shutdown logic

app = FastAPI(title="DSP Analyzer API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(filters.router)
app.include_router(analysis.router)
app.include_router(coherence.router)
app.include_router(io_routes.router)
app.include_router(signals.router)

@app.get("/health")
def health():
    return {"status": "ok", "version": "0.1.0"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("API_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
