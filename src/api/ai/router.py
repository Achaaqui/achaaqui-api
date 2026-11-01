from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from langchain_core.messages import AIMessage, HumanMessage
from sqlalchemy.ext.asyncio import AsyncSession

from src.ai.workflows.search.title_agent import generate_conversation_title
from src.ai.workflows.search.schemas import (
    AgentRequest,
    AgentResponse,
    ConversationMessage,
    ConversationResponse,
    ConversationSummary,
)
from src.database import get_db_session
from src.dependencies.auth import get_current_user
from src.repositories.conversation_repository import ConversationRepository
from src.services.conversation_service import ConversationService

router = APIRouter(
    prefix="/ai"
)


def _content_to_text(content: object) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            block.get("text", "")
            for block in content
            if isinstance(block, dict) and isinstance(block.get("text"), str)
        )
    return ""


def _conversation_config(user_email: str, conversation_id: object) -> dict:
    return {"configurable": {"thread_id": f"{user_email}:{conversation_id}"}}


def _get_conversation_messages(messages: list[object]) -> list[ConversationMessage]:
    conversation: list[ConversationMessage] = []
    for message in messages:
        if isinstance(message, HumanMessage):
            role = "user"
        elif isinstance(message, AIMessage):
            role = "assistant"
        else:
            continue

        content = _content_to_text(message.content)
        if content.strip():
            conversation.append(ConversationMessage(role=role, content=content))
    return conversation


def get_conversation_service(
    session: AsyncSession = Depends(get_db_session),
) -> ConversationService:
    return ConversationService(ConversationRepository(session))


async def _save_conversation(
    conversation_service: ConversationService,
    conversation_id: str,
    user_email: str,
    prompt: str,
) -> None:
    conversation = await conversation_service.get(conversation_id, user_email)
    if conversation is not None:
        await conversation_service.touch(conversation)
        return

    title = await generate_conversation_title(prompt)
    await conversation_service.create(conversation_id, user_email, title)


@router.post("/research", response_model=AgentResponse)
async def research(
    request: AgentRequest,
    fastapi_request: Request,
    user_email: str = Depends(get_current_user),
    conversation_service: ConversationService = Depends(get_conversation_service),
) -> AgentResponse:
    agent = fastapi_request.app.state.search_agent
    await _save_conversation(
        conversation_service, str(request.conversation_id), user_email, request.prompt
    )

    result = await agent.ainvoke(
        {"messages": [HumanMessage(content=request.prompt)]},
        config=_conversation_config(user_email, request.conversation_id),
    )

    final_message = result["messages"][-1]
    content = final_message.content
    answer = content if isinstance(content, str) else str(content)

    return AgentResponse(answer=answer)


@router.post("/research/stream")
async def research_stream(
    request: AgentRequest,
    fastapi_request: Request,
    user_email: str = Depends(get_current_user),
    conversation_service: ConversationService = Depends(get_conversation_service),
) -> StreamingResponse:
    agent = fastapi_request.app.state.search_agent
    config = _conversation_config(user_email, request.conversation_id)
    await _save_conversation(
        conversation_service, str(request.conversation_id), user_email, request.prompt
    )

    async def stream_answer() -> AsyncIterator[str]:
        async for message, metadata in agent.astream(
            {"messages": [HumanMessage(content=request.prompt)]},
            config=config,
            stream_mode="messages",
        ):
            if metadata.get("langgraph_node") != "model":
                continue
            text = _content_to_text(message.content)
            if text:
                yield text

    return StreamingResponse(
        stream_answer(),
        media_type="text/plain; charset=utf-8",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/conversations", response_model=list[ConversationSummary])
async def list_conversations(
    user_email: str = Depends(get_current_user),
    conversation_service: ConversationService = Depends(get_conversation_service),
) -> list[ConversationSummary]:
    conversations = await conversation_service.list_by_user(user_email)
    return [
        ConversationSummary(
            id=conversation.id,
            title=conversation.title,
            updated_at=conversation.updated_at,
        )
        for conversation in conversations
    ]


@router.get("/conversations/{conversation_id}/messages", response_model=ConversationResponse)
async def get_conversation_messages(
    conversation_id: str,
    fastapi_request: Request,
    user_email: str = Depends(get_current_user),
) -> ConversationResponse:
    agent = fastapi_request.app.state.search_agent
    state = await agent.aget_state(_conversation_config(user_email, conversation_id))
    messages = state.values.get("messages", [])

    return ConversationResponse(
        conversation_id=conversation_id,
        messages=_get_conversation_messages(messages),
    )
