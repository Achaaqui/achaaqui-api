from typing import Any

from tavily import TavilyClient as TavilySDKClient

from src.config import settings


class TavilyClient:
    """Application client that encapsulates the official Tavily SDK."""

    def __init__(self, api_key: str | None = None) -> None:
        self._api_key = api_key or settings.TAVILY_API_KEY
        self._client: TavilySDKClient | None = None

    def search(self, query: str) -> dict[str, Any]:
        response = self._get_client().search(
            query=query,
            topic="general",
            max_results=6,
            include_answer=True,
        )
        return {
            "answer": response.get("answer"),
            "results": [
                {
                    "title": result.get("title"),
                    "url": result.get("url"),
                    "content": result.get("content"),
                    "score": result.get("score"),
                }
                for result in response.get("results", [])
            ],
        }

    def extract(self, urls: list[str]) -> dict[str, Any]:
        """Open Tavily search-result URLs and return their useful page content."""
        unique_urls = list(dict.fromkeys(url for url in urls if url.startswith("http")))[:3]
        if not unique_urls:
            return {"results": [], "failed_results": []}

        response = self._get_client().extract(
            urls=unique_urls,
            extract_depth="advanced",
            format="markdown",
        )
        return {
            "results": [
                {
                    "url": result.get("url"),
                    "title": result.get("title"),
                    "content": (result.get("raw_content") or result.get("content") or "")[:8000],
                }
                for result in response.get("results", [])
            ],
            "failed_results": [
                {"url": result.get("url"), "error": result.get("error")}
                for result in response.get("failed_results", [])
            ],
        }

    def _get_client(self) -> TavilySDKClient:
        if not self._api_key:
            raise ValueError("TAVILY_API_KEY is not configured")
        if self._client is None:
            self._client = TavilySDKClient(api_key=self._api_key)
        return self._client


tavily_client = TavilyClient()
