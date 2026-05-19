from fastapi import APIRouter

router = APIRouter(prefix="/filters", tags=["filters"])

@router.post("/apply")
async def apply_filter():
    return {"message": "placeholder"}