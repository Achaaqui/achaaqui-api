from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field


class AgentRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=8_000)
    conversation_id: UUID


class AgentResponse(BaseModel):
    answer: str


class ConversationMessage(BaseModel):
    role: str
    content: str


class ConversationResponse(BaseModel):
    conversation_id: UUID
    messages: list[ConversationMessage]


class ConversationSummary(BaseModel):
    id: UUID
    title: str
    updated_at: datetime
