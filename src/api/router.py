from fastapi import APIRouter

from src.api.ai.router import router as ai_router
from src.api.auth.router import router as auth_router

router = APIRouter(prefix="/api")

router.include_router(auth_router)
router.include_router(ai_router)
