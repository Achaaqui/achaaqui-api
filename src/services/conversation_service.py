from src.models.conversation import Conversation
from src.repositories.conversation_repository import ConversationRepository


class ConversationService:
    def __init__(self, repository: ConversationRepository) -> None:
        self._repository = repository

    async def get(self, conversation_id: str, user_email: str) -> Conversation | None:
        return await self._repository.get(conversation_id, user_email)

    async def create(
        self, conversation_id: str, user_email: str, title: str
    ) -> Conversation:
        return await self._repository.create(conversation_id, user_email, title)

    async def touch(self, conversation: Conversation) -> Conversation:
        return await self._repository.touch(conversation)

    async def list_by_user(self, user_email: str) -> list[Conversation]:
        return await self._repository.list_by_user(user_email)
