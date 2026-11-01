from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.conversation import Conversation


class ConversationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, conversation_id: str, user_email: str) -> Conversation | None:
        return await self._session.scalar(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_email == user_email,
            )
        )

    async def create(
        self, conversation_id: str, user_email: str, title: str
    ) -> Conversation:
        conversation = Conversation(
            id=conversation_id,
            user_email=user_email,
            title=title[:200],
        )
        self._session.add(conversation)

        await self._session.commit()
        await self._session.refresh(conversation)
        return conversation

    async def touch(self, conversation: Conversation) -> Conversation:
        conversation.updated_at = datetime.now(timezone.utc)

        await self._session.commit()
        await self._session.refresh(conversation)
        return conversation

    async def list_by_user(self, user_email: str) -> list[Conversation]:
        result = await self._session.scalars(
            select(Conversation)
            .where(Conversation.user_email == user_email)
            .order_by(Conversation.updated_at.desc())
        )
        return list(result)
