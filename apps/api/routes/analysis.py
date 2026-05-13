from fastapi import APIRouter

router = APIRouter(prefix="/analysis", tags=["analysis"])

@router.post("/fft")
async def compute_fft():
    return {"message": "placeholder"}