from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth.schemas import LoginRequest, SignupRequest, TokenResponse
from src.api.responses import service_error_response
from src.database import get_db_session
from src.repositories.auth_repository import AuthRepository
from src.services.auth_service import AuthService

router = APIRouter(
    prefix="/auth"
)


def get_auth_service(
    session: AsyncSession = Depends(get_db_session),
) -> AuthService:
    return AuthService(AuthRepository(session))


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: LoginRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    try:
        return await service.login(credentials)
    except Exception as error:
        return service_error_response(error)


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    payload: SignupRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    try:
        return await service.signup(payload)
    except Exception as error:
        return service_error_response(error)
