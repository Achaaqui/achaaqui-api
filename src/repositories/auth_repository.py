from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User


class AuthRepository:
    """Persistence operations for authentication entities."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_email(self, email: str) -> User | None:
        return await self._session.scalar(
            select(User).where(User.email == email)
        )

    async def create(self, username: str, email: str, password_hash: str) -> User:
        user = User(username=username, email=email, password_hash=password_hash)
        self._session.add(user)
        await self._session.commit()
        await self._session.refresh(user)
        return user

    async def rollback(self) -> None:
        await self._session.rollback()
