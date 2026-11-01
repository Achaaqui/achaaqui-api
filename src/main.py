from fastapi import FastAPI

from src.ai.checkpointer import agent_lifespan
from src.api.router import router as api_router


def create_app() -> FastAPI:
    app = FastAPI(lifespan=agent_lifespan)
    app.include_router(api_router)
    return app

app = create_app()
