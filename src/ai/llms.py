from langchain_openai import ChatOpenAI

from src.config import settings

gpt_6_luna = ChatOpenAI(
    model="gpt-6-luna",
    api_key=settings.OPENAI_API_KEY,
)
