from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URL: str = "sqlite+aiosqlite:///./achaaqui.db"
    LANGGRAPH_DATABASE_URL: str | None = None
    OPENAI_API_KEY: str
    TAVILY_API_KEY: str


settings = Settings()


def get_langgraph_database_url() -> str:
    database_url = settings.LANGGRAPH_DATABASE_URL or settings.DATABASE_URL
    if database_url.startswith("postgresql+asyncpg://"):
        return database_url.replace("postgresql+asyncpg://", "postgresql://", 1)
    if database_url.startswith("postgresql://"):
        return database_url
    raise ValueError("LangGraph persistent memory requires a PostgreSQL DATABASE_URL")
