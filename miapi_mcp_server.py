"""
MIAPI MCP Server
Lets AI assistants (Claude Desktop, Cursor, Windsurf, etc.)
use MIAPI for web-grounded AI answers with citations.

Install:
    pip install "mcp[cli]" httpx

Run:
    python miapi_mcp_server.py

Or configure in Claude Desktop / Cursor config.
"""

import os
import json
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize MCP server
mcp = FastMCP(
    "miapi",
    description="MIAPI - Web-grounded AI answers with real-time citations. Search the web and get sourced answers in one call."
)

API_BASE = os.environ.get("MIAPI_BASE_URL", "https://api.miapi.uk")
API_KEY = os.environ.get("MIAPI_API_KEY", "")

def _headers():
    return {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }


@mcp.tool()
async def web_answer(question: str, temperature: float = 0.3) -> str:
    """
    Get a web-grounded AI answer with inline citations.
    Searches the web in real-time, synthesizes an answer, and returns
    it with [1][2] source citations and source URLs.

    Args:
        question: The question to answer (e.g. "Who won the 2024 Super Bowl?")
        temperature: LLM temperature 0.0-1.0 (default 0.3 for factual)
    """
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(f"{API_BASE}/v1/answer", headers=_headers(), json={
            "question": question,
            "temperature": temperature,
            "citations": True,
        })
        if r.status_code != 200:
            return f"Error {r.status_code}: {r.text}"
        d = r.json()

    answer = d.get("answer", "No answer")
    sources = d.get("sources", [])
    confidence = d.get("confidence", 0)
    ms = d.get("query_time_ms", 0)

    result = f"{answer}\n\n"
    if sources:
        result += "Sources:\n"
        for i, s in enumerate(sources, 1):
            result += f"[{i}] {s.get('title', 'Untitled')} - {s.get('url', '')}\n"
    result += f"\nConfidence: {confidence:.0%} | Time: {ms}ms"
    return result


@mcp.tool()
async def web_search(query: str, num_results: int = 7) -> str:
    """
    Search the web and return raw results (titles, URLs, snippets).
    Use this when you need search results without AI synthesis.

    Args:
        query: Search query (e.g. "latest AI news March 2026")
        num_results: Number of results to return (1-10, default 7)
    """
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(f"{API_BASE}/v1/search", headers=_headers(), json={
            "query": query,
            "num_results": min(num_results, 10),
        })
        if r.status_code != 200:
            return f"Error {r.status_code}: {r.text}"
        d = r.json()

    results = d.get("results", [])
    if not results:
        return "No results found."

    output = ""
    for i, res in enumerate(results, 1):
        output += f"[{i}] {res.get('title', 'Untitled')}\n"
        output += f"    {res.get('url', '')}\n"
        output += f"    {res.get('snippet', '')}\n\n"
    return output.strip()


@mcp.tool()
async def news_search(query: str, num_results: int = 5) -> str:
    """
    Search for recent news articles on a topic.

    Args:
        query: News topic to search (e.g. "OpenAI GPT-5")
        num_results: Number of articles to return (1-10, default 5)
    """
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(f"{API_BASE}/v1/news", headers=_headers(), json={
            "query": query,
            "num_results": min(num_results, 10),
        })
        if r.status_code != 200:
            return f"Error {r.status_code}: {r.text}"
        d = r.json()

    articles = d.get("articles", [])
    if not articles:
        return "No news articles found."

    output = ""
    for i, a in enumerate(articles, 1):
        output += f"[{i}] {a.get('title', 'Untitled')}\n"
        output += f"    {a.get('url', '')}\n"
        output += f"    {a.get('snippet', a.get('description', ''))}\n"
        if a.get("date"):
            output += f"    Published: {a['date']}\n"
        output += "\n"
    return output.strip()


@mcp.tool()
async def image_search(query: str, num_results: int = 5) -> str:
    """
    Search for images on the web.

    Args:
        query: Image search query (e.g. "golden gate bridge sunset")
        num_results: Number of images to return (1-10, default 5)
    """
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(f"{API_BASE}/v1/images", headers=_headers(), json={
            "query": query,
            "num_results": min(num_results, 10),
        })
        if r.status_code != 200:
            return f"Error {r.status_code}: {r.text}"
        d = r.json()

    images = d.get("images", [])
    if not images:
        return "No images found."

    output = ""
    for i, img in enumerate(images, 1):
        output += f"[{i}] {img.get('title', 'Untitled')}\n"
        output += f"    Image: {img.get('imageUrl', img.get('url', ''))}\n"
        output += f"    Source: {img.get('link', img.get('source', ''))}\n\n"
    return output.strip()


@mcp.tool()
async def check_usage() -> str:
    """
    Check your MIAPI API usage and remaining query balance.
    No arguments needed.
    """
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(f"{API_BASE}/v1/usage", headers=_headers())
        if r.status_code != 200:
            return f"Error {r.status_code}: {r.text}"
        d = r.json()

    return (
        f"Queries today: {d.get('queries_today', 0)}\n"
        f"Queries this month: {d.get('queries_this_month', 0)}\n"
        f"Queries remaining: {d.get('queries_remaining', 0):,}\n"
        f"Rate limit: {d.get('rate_limit_per_minute', 0)}/min\n"
        f"Paid account: {'Yes' if d.get('has_purchased') else 'No'}"
    )


if __name__ == "__main__":
    mcp.run()
