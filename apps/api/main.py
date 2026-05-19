from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import filters, analysis, coherence

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:1420", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(filters.router)
app.include_router(analysis.router)
app.include_router(coherence.router)

@app.get("/health")
async def health():
    return {"status": "ok"}