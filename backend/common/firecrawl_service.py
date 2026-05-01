"""
Firecrawl Service — v2 API with multi-source search, crawl, map, and streaming AI.
"""

import asyncio
import json
import httpx
from config import FIRECRAWL_API_KEY, FREELLM_API_KEY, FREELLM_BASE_URL, DEFAULT_MODEL


class FirecrawlService:
    def __init__(self):
        self.api_key = FIRECRAWL_API_KEY
        self.base_url = "https://api.firecrawl.dev/v2"
        self.ai_api_key = FREELLM_API_KEY
        self.ai_base_url = FREELLM_BASE_URL
        self.ai_model = DEFAULT_MODEL
        self._headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    # ─── Search (v2 multi-source) ─────────────────────────────
    async def search(self, query: str, limit: int = 6, sources: list[str] | None = None):
        """Search via Firecrawl v2 — supports web, news, images sources."""
        payload = {
            "query": query,
            "limit": limit,
            "scrapeOptions": {
                "formats": ["markdown"],
                "onlyMainContent": True,
            },
        }
        if sources:
            payload["sources"] = sources  # e.g. ["web", "news", "images"]

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/search",
                json=payload,
                headers=self._headers,
            )
            response.raise_for_status()
            return response.json()

    # ─── Scrape ───────────────────────────────────────────────
    async def scrape(self, url: str, timeout_ms: int = 15000):
        """Scrape a single URL for markdown content."""
        async with httpx.AsyncClient(timeout=timeout_ms / 1000) as client:
            response = await client.post(
                f"{self.base_url}/scrape",
                json={"url": url, "formats": ["markdown"]},
                headers=self._headers,
            )
            response.raise_for_status()
            return response.json()

    # ─── Crawl ────────────────────────────────────────────────
    async def crawl(self, url: str, limit: int = 20):
        """Start a crawl job. Returns job ID for polling."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/crawl",
                json={
                    "url": url,
                    "limit": limit,
                    "scrapeOptions": {"formats": ["markdown"]},
                },
                headers=self._headers,
            )
            response.raise_for_status()
            return response.json()

    async def crawl_status(self, job_id: str):
        """Check crawl job status."""
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                f"{self.base_url}/crawl/{job_id}",
                headers=self._headers,
            )
            response.raise_for_status()
            return response.json()

    # ─── Map ──────────────────────────────────────────────────
    async def map_url(self, url: str, limit: int = 50):
        """Discover all URLs on a site."""
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                f"{self.base_url}/map",
                json={"url": url, "limit": limit},
                headers=self._headers,
            )
            response.raise_for_status()
            return response.json()

    # ─── AI Answer (non-streaming) ────────────────────────────
    async def answer_with_ai(self, query: str, search_results: dict) -> str:
        """Generate an AI summary from search results using FreeLLMAPI."""
        context = ""
        data = search_results.get("data", {})
        # v2 returns {"data": {"web": [...], "news": [...], "images": [...]}}
        web_items = data.get("web", []) if isinstance(data, dict) else data if isinstance(data, list) else []

        for item in web_items[:5]:
            content = item.get("markdown") or item.get("content") or ""
            context += f"\nSource: {item.get('url')}\nContent: {content[:1000]}\n"

        prompt = (
            f"User Query: {query}\n\n"
            f"Web Search Context:\n{context}\n\n"
            "Provide a comprehensive, well-structured answer. "
            "Use markdown formatting. Include inline citations like [1], [2]."
        )

        headers = {
            "Authorization": f"Bearer {self.ai_api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.ai_base_url}/chat/completions",
                json={
                    "model": self.ai_model,
                    "messages": [{"role": "user", "content": prompt}],
                },
                headers=headers,
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]

    # ─── AI Answer (streaming via SSE) ────────────────────────
    async def stream_ai_answer(self, query: str, search_results: dict):
        """
        Yields SSE-formatted chunks of the AI answer.
        Each chunk is a string like: data: {"chunk": "..."}\n\n
        """
        context = ""
        data = search_results.get("data", {})
        web_items = data.get("web", []) if isinstance(data, dict) else data if isinstance(data, list) else []

        for i, item in enumerate(web_items[:6]):
            content = item.get("markdown") or item.get("content") or ""
            url = item.get("url", "")
            title = item.get("title", url)
            context += f"\n[{i + 1}] {title}\nURL: {url}\n{content[:1500]}\n"

        system_prompt = (
            "You are a helpful assistant that answers questions using web search results.\n\n"
            "RULES:\n"
            "- Use markdown formatting for readability\n"
            "- Include inline citations as [1], [2], etc. referencing source order\n"
            "- Be concise but thorough\n"
            "- NEVER use LaTeX math syntax for regular numbers\n"
            "- Write numbers as plain text: '1 million' NOT '$1$ million'"
        )

        headers = {
            "Authorization": f"Bearer {self.ai_api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                f"{self.ai_base_url}/chat/completions",
                json={
                    "model": self.ai_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f'Answer: "{query}"\n\nSources:\n{context}'},
                    ],
                    "stream": True,
                },
                headers=headers,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        payload = line[6:]
                        if payload.strip() == "[DONE]":
                            break
                        try:
                            chunk_data = json.loads(payload)
                            choices = chunk_data.get("choices", [])
                            if choices:
                                delta = choices[0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    yield content
                        except json.JSONDecodeError:
                            continue

    # ─── Follow-up Questions ──────────────────────────────────
    async def generate_follow_ups(self, query: str, answer: str) -> list[str]:
        """Generate follow-up questions based on query and answer."""
        headers = {
            "Authorization": f"Bearer {self.ai_api_key}",
            "Content-Type": "application/json",
        }

        prompt = (
            f"Based on this query and answer, generate 4 natural follow-up questions.\n\n"
            f"Query: {query}\n"
            f"Answer: {answer[:500]}\n\n"
            "Return only the questions, one per line, no numbering."
        )

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.ai_base_url}/chat/completions",
                    json={
                        "model": self.ai_model,
                        "messages": [{"role": "user", "content": prompt}],
                    },
                    headers=headers,
                )
                response.raise_for_status()
                text = response.json()["choices"][0]["message"]["content"]
                return [q.strip() for q in text.strip().split("\n") if q.strip()][:4]
        except Exception:
            return []
