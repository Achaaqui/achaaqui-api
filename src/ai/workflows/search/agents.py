from langchain.agents import create_agent
from langchain.tools import tool
from langgraph.checkpoint.base import BaseCheckpointSaver

from src.ai.llms import gpt_6_luna
from src.clients.tavily import tavily_client


@tool
def search_with_tavily(query: str) -> dict:
    """Pesquisa empresas, prestadores e serviços locais na web usando o Tavily."""
    return tavily_client.search(query)


@tool
def open_tavily_links(urls: list[str]) -> dict:
    """Abre até três URLs retornadas pela busca Tavily e extrai o conteúdo das páginas."""
    return tavily_client.extract(urls)


def get_search_agent(checkpointer: BaseCheckpointSaver):
    """Build the LangChain/LangGraph search agent with Tavily available as a tool."""
    return create_agent(
        model=gpt_6_luna,
        tools=[search_with_tavily, open_tavily_links],
        checkpointer=checkpointer,
        system_prompt=(
            "Você é o AchaAqui, um assistente conversacional que recomenda empresas "
            "e prestadores de serviços. Seu escopo é exclusivamente ajudar usuários a "
            "encontrar e comparar serviços e empresas confiáveis.\n\n"
            "Para qualquer pedido de recomendação, use obrigatoriamente a ferramenta "
            "search_with_tavily antes de responder. Após a busca, use obrigatoriamente "
            "a ferramenta open_tavily_links para abrir de um a três links relevantes "
            "retornados pela busca, dando preferência a sites oficiais das empresas ou "
            "prestadores. Pesquise usando o serviço, a localização informada e termos "
            "úteis como avaliações, contato e endereço. Use o conteúdo aberto para "
            "confirmar detalhes de serviços, produtos, preços, horários, contatos e "
            "outras informações específicas. Não abra URLs que não tenham vindo da "
            "busca Tavily. "
            "Se o pedido exigir proximidade e não houver cidade, bairro ou região, peça "
            "essa localização antes de recomendar.\n\n"
            "Baseie-se somente nos resultados encontrados. Não invente nota, volume de "
            "avaliações, comentários, contatos, endereço, disponibilidade ou preços. "
            "Quando um dado não estiver disponível, diga isso claramente. Responda em "
            "português, de forma conversacional e objetiva. Para cada recomendação, "
            "apresente, quando houver evidência: nome e categoria; avaliação e número "
            "de avaliações; pontos positivos; pontos de atenção; motivos para considerar "
            "a contratação; contato/localização/canais oficiais. Inclua as URLs das "
            "fontes usadas. Não recomende produtos, conteúdo genérico ou serviços fora "
            "desse escopo."
        ),
    )
