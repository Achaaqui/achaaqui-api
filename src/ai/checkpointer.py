from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from src.ai.workflows.search.agents import get_search_agent
from src.config import get_langgraph_database_url


@asynccontextmanager
async def agent_lifespan(app: FastAPI) -> AsyncIterator[None]:
    async with AsyncPostgresSaver.from_conn_string(
        get_langgraph_database_url()
    ) as checkpointer:
        await checkpointer.setup()
        app.state.search_agent = get_search_agent(checkpointer)
        yield
