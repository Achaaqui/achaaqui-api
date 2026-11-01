import re

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage

from src.ai.llms import gpt_6_luna

_FALLBACK_TITLE_LENGTH = 72

_title_agent = create_agent(
    model=gpt_6_luna,
    tools=[],
    system_prompt=(
        "Crie um título curto, útil e natural em português para a conversa a partir da "
        "mensagem do usuário. Responda somente com o título, sem aspas, Markdown, "
        "pontuação final ou explicações. Use no máximo 8 palavras."
    ),
)


def _fallback_title(prompt: str) -> str:
    normalized_prompt = " ".join(prompt.split())
    return normalized_prompt[:_FALLBACK_TITLE_LENGTH] or "Nova conversa"


async def generate_conversation_title(prompt: str) -> str:
    """Generate a concise conversation title without preventing the research flow."""
    try:
        result = await _title_agent.ainvoke(
            {"messages": [HumanMessage(content=prompt)]}
        )
        content = result["messages"][-1].content
        if not isinstance(content, str):
            return _fallback_title(prompt)

        title = re.sub(r"\s+", " ", content).strip().strip("\"'").rstrip(".?!")
        return title[:_FALLBACK_TITLE_LENGTH] or _fallback_title(prompt)
    except Exception:
        return _fallback_title(prompt)
