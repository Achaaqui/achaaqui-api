from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash
from sqlalchemy.exc import IntegrityError

from src.api.auth.schemas import LoginRequest, SignupRequest, TokenResponse
from src.config import settings
from src.expections.service import ServiceError
from src.repositories.auth_repository import AuthRepository


class AuthService:
    def __init__(self, repository: AuthRepository) -> None:
        self._repository = repository
        self._password_hash = PasswordHash.recommended()

    async def login(self, credentials: LoginRequest) -> TokenResponse:
        user = await self._repository.get_by_email(credentials.email)
        if user is None or not self._verify_password(
            credentials.password, user.password_hash
        ):
            raise ServiceError("E-mail ou senha incorretos")
        return TokenResponse(access_token=self._create_access_token(user.email))

    async def signup(self, payload: SignupRequest) -> TokenResponse:
        if await self._repository.get_by_email(payload.email):
            raise ServiceError("Email is already registered")
        try:
            user = await self._repository.create(
                username=payload.username,
                email=payload.email,
                password_hash=self._hash_password(payload.password),
            )
        except IntegrityError as error:
            await self._repository.rollback()
            raise ServiceError("Username or email is already registered") from error
        return TokenResponse(access_token=self._create_access_token(user.email))

    def _hash_password(self, password: str) -> str:
        return self._password_hash.hash(password)

    def _verify_password(self, password: str, hashed_password: str) -> bool:
        return self._password_hash.verify(password, hashed_password)

    def _create_access_token(self, subject: str) -> str:
        if not settings.JWT_SECRET_KEY:
            raise ServiceError("JWT_SECRET_KEY is not configured")
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        return jwt.encode(
            {"sub": subject, "exp": expires_at},
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )
