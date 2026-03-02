"""
MIAPI — Grounded AI Answers API Client

Get AI-powered answers grounded in real-time web search.
Inline citations, knowledge mode, streaming, and more.

Usage:
    from miapi import MIAPI

    client = MIAPI("YOUR_API_KEY")
    result = client.answer("What is quantum computing?", citations=True)
    print(result.answer)
    print(result.sources)
"""

import requests
from dataclasses import dataclass, field
from typing import Optional, List, Generator


@dataclass
class Source:
    """A source used to ground the answer."""
    title: str = ""
    url: str = ""
    snippet: str = ""


@dataclass
class AnswerResult:
    """Result from the answer endpoint."""
    answer: str = ""
    sources: List[Source] = field(default_factory=list)
    confidence: float = 0.0
    cached: bool = False
    query_time_ms: int = 0
    mode: str = "answer"
    request_id: str = ""


@dataclass
class NewsArticle:
    """A news article result."""
    title: str = ""
    url: str = ""
    snippet: str = ""
    date: str = ""
    source: str = ""


@dataclass
class Image:
    """An image search result."""
    title: str = ""
    url: str = ""
    source: str = ""
    thumbnail: str = ""
    width: int = 0
    height: int = 0


@dataclass
class UsageInfo:
    """API usage information."""
    queries_today: int = 0
    queries_this_month: int = 0
    rate_limit_per_minute: int = 0
    tier: str = "free"
    monthly_limit: int = 500


class MIAPIError(Exception):
    """Base exception for MIAPI errors."""
    def __init__(self, message: str, status_code: int = 0):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class RateLimitError(MIAPIError):
    """Raised when rate limit is exceeded."""
    pass


class AuthenticationError(MIAPIError):
    """Raised when API key is invalid."""
    pass


class MIAPI:
    """
    MIAPI client for grounded AI answers.

    Args:
        api_key: Your MIAPI API key (starts with 'gapi_')
        base_url: API base URL (default: https://api.miapi.uk)
        timeout: Request timeout in seconds (default: 30)

    Example:
        >>> client = MIAPI("gapi_your_key_here")
        >>> result = client.answer("What is CRISPR?", citations=True)
        >>> print(result.answer)
        >>> print(result.sources)
    """

    def __init__(self, api_key: str, base_url: str = "https://api.miapi.uk", timeout: int = 30):
        if not api_key:
            raise AuthenticationError("API key is required.")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "miapi-python/1.0.0",
        })

    def _request(self, method: str, path: str, json_data: dict = None) -> dict:
        """Make a request to the MIAPI API."""
        url = f"{self.base_url}{path}"
        try:
            resp = self._session.request(method, url, json=json_data, timeout=self.timeout)
        except requests.ConnectionError:
            raise MIAPIError("Could not connect to MIAPI. Check your internet connection.")
        except requests.Timeout:
            raise MIAPIError("Request timed out. Try again or increase timeout.")

        if resp.status_code == 401:
            raise AuthenticationError("Invalid API key.", status_code=401)
        if resp.status_code == 429:
            detail = resp.json().get("detail", {})
            msg = detail.get("message", "Rate limit exceeded.") if isinstance(detail, dict) else str(detail)
            raise RateLimitError(msg, status_code=429)
        if resp.status_code >= 400:
            detail = resp.json().get("detail", "Unknown error")
            raise MIAPIError(str(detail), status_code=resp.status_code)

        return resp.json()

    def answer(
        self,
        question: str,
        *,
        mode: str = "answer",
        citations: bool = False,
        knowledge: str = "",
        system_prompt: str = "",
        response_format: str = "text",
        temperature: float = None,
        max_tokens: int = None,
        include_sources: bool = True,
        search_domains: list = None,
        language: str = "",
        context: list = None,
    ) -> AnswerResult:
        """
        Get a grounded AI answer.

        Args:
            question: The question to answer (2-1000 chars)
            mode: 'answer' (default), 'search' (raw results), 'knowledge' (from your text)
            citations: Include [1][2] citation markers in the answer
            knowledge: Custom context for the LLM (up to 10K chars)
            system_prompt: Custom system prompt (max 2000 chars)
            response_format: 'text', 'short', 'json', or 'markdown'
            temperature: 0.0 to 1.0 (default 0.3)
            max_tokens: 50-2000 (auto if not set)
            include_sources: Include source URLs (default True)
            search_domains: Restrict search to specific domains
            language: Force response language (e.g. 'Spanish')
            context: Conversation history for follow-ups

        Returns:
            AnswerResult with answer, sources, confidence, etc.

        Example:
            >>> result = client.answer("What is CRISPR?", citations=True)
            >>> print(result.answer)
            >>> for s in result.sources:
            ...     print(s.url)
        """
        body = {
            "question": question,
            "mode": mode,
            "citations": citations,
            "include_sources": include_sources,
            "response_format": response_format,
        }
        if knowledge:
            body["knowledge"] = knowledge
        if system_prompt:
            body["system_prompt"] = system_prompt
        if temperature is not None:
            body["temperature"] = temperature
        if max_tokens is not None:
            body["max_tokens"] = max_tokens
        if search_domains:
            body["search_domains"] = search_domains
        if language:
            body["language"] = language
        if context:
            body["context"] = context

        data = self._request("POST", "/v1/answer", body)

        sources = [Source(**s) for s in data.get("sources", [])]
        return AnswerResult(
            answer=data.get("answer", ""),
            sources=sources,
            confidence=data.get("confidence", 0.0),
            cached=data.get("cached", False),
            query_time_ms=data.get("query_time_ms", 0),
            mode=data.get("mode", "answer"),
            request_id=data.get("request_id", ""),
        )

    def search(self, query: str, *, include_sources: bool = True) -> List[Source]:
        """
        Search the web and return raw results (no AI answer).

        Args:
            query: Search query
            include_sources: Include source details (default True)

        Returns:
            List of Source objects with title, url, snippet

        Example:
            >>> results = client.search("latest AI research papers")
            >>> for source in results:
            ...     print(source.url)
        """
        result = self.answer(query, mode="search", include_sources=include_sources)
        return result.sources

    def news(self, query: str, *, num_results: int = 5) -> List[NewsArticle]:
        """
        Search for recent news articles.

        Args:
            query: News search query
            num_results: Number of results (1-20, default 5)

        Returns:
            List of NewsArticle objects

        Example:
            >>> news = client.news("technology", num_results=5)
            >>> for article in news:
            ...     print(article.title, article.date)
        """
        data = self._request("POST", "/v1/news", {
            "query": query,
            "num_results": num_results,
        })
        return [NewsArticle(**a) for a in data.get("articles", [])]

    def images(self, query: str, *, num_results: int = 5) -> List[Image]:
        """
        Search for images.

        Args:
            query: Image search query
            num_results: Number of results (1-20, default 5)

        Returns:
            List of Image objects

        Example:
            >>> images = client.images("golden retriever")
            >>> for img in images:
            ...     print(img.url, img.width, img.height)
        """
        data = self._request("POST", "/v1/images", {
            "query": query,
            "num_results": num_results,
        })
        return [Image(**i) for i in data.get("images", [])]

    def usage(self) -> UsageInfo:
        """
        Check your API usage stats.

        Returns:
            UsageInfo with queries today, this month, rate limit, tier

        Example:
            >>> info = client.usage()
            >>> print(f"Used {info.queries_this_month}/{info.monthly_limit} this month")
        """
        data = self._request("GET", "/v1/usage")
        return UsageInfo(
            queries_today=data.get("queries_today", 0),
            queries_this_month=data.get("queries_this_month", 0),
            rate_limit_per_minute=data.get("rate_limit_per_minute", 0),
            tier=data.get("tier", "free"),
            monthly_limit=data.get("monthly_limit", 500),
        )

    def stream(
        self,
        question: str,
        *,
        system_prompt: str = "",
        temperature: float = None,
        max_tokens: int = None,
        include_sources: bool = True,
        knowledge: str = "",
        citations: bool = False,
        language: str = "",
    ) -> Generator[dict, None, None]:
        """
        Stream an AI answer via Server-Sent Events.

        Yields dicts with 'type' key: 'sources', 'answer', 'done'

        Args:
            question: The question to answer
            system_prompt: Custom system prompt
            temperature: 0.0 to 1.0
            max_tokens: 50-2000
            include_sources: Include sources
            knowledge: Custom context
            citations: Include citation markers
            language: Response language

        Example:
            >>> for event in client.stream("Explain quantum computing"):
            ...     if event['type'] == 'answer':
            ...         print(event['content'], end='', flush=True)
            ...     elif event['type'] == 'done':
            ...         print(f"\\nDone in {event.get('query_time_ms')}ms")
        """
        import json

        body = {
            "question": question,
            "include_sources": include_sources,
            "citations": citations,
        }
        if system_prompt:
            body["system_prompt"] = system_prompt
        if temperature is not None:
            body["temperature"] = temperature
        if max_tokens is not None:
            body["max_tokens"] = max_tokens
        if knowledge:
            body["knowledge"] = knowledge
        if language:
            body["language"] = language

        url = f"{self.base_url}/v1/stream"
        resp = self._session.post(url, json=body, stream=True, timeout=self.timeout)

        if resp.status_code != 200:
            raise MIAPIError(f"Stream error: HTTP {resp.status_code}", status_code=resp.status_code)

        for line in resp.iter_lines(decode_unicode=True):
            if line and line.startswith("data: "):
                try:
                    event = json.loads(line[6:])
                    yield event
                except json.JSONDecodeError:
                    continue

    def __repr__(self):
        masked = self.api_key[:8] + "..." + self.api_key[-4:] if len(self.api_key) > 12 else "***"
        return f"MIAPI(api_key='{masked}', base_url='{self.base_url}')"
