from fastapi import APIRouter

router = APIRouter(
    prefix="/ai"
)


@router.post("/test")
async def test():
    return {"ok": True}
