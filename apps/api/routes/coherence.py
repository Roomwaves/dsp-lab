from fastapi import APIRouter

router = APIRouter(prefix="/coherence", tags=["coherence"])

@router.post("/")
async def compute_coherence():
    return {"message": "placeholder"}