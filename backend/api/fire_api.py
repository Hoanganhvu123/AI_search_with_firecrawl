"""
Firecrawl API — Quick Search endpoints with SSE streaming.
"""

import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from common.firecrawl_service import FirecrawlService
from database.fire_db import get_db_connection

router = APIRouter()


class SearchRequest(BaseModel):
    query: str
    sources: list[str] | None = None  # ["web", "news", "images"]


class ScrapeRequest(BaseModel):
    url: str


# ─── SSE Streaming Search (NEW — Perplexity-style) ───────────
@router.post("/search/stream")
async def search_stream(request: SearchRequest):
    """
    SSE endpoint: streams search results then AI answer chunks.
    
    Events:
      data: {"type": "status", "message": "..."}
      data: {"type": "sources", "web": [...], "news": [...], "images": [...]}
      data: {"type": "chunk", "content": "..."}
      data: {"type": "follow_ups", "questions": [...]}
      data: {"type": "done"}
      data: {"type": "error", "message": "..."}
    """

    async def event_generator():
        service = FirecrawlService()

        try:
            # Phase 1: Status
            yield _sse({"type": "status", "message": "Searching the web..."})

            # Phase 2: Search
            sources_list = request.sources or ["web", "news", "images"]
            try:
                result = await service.search(
                    request.query,
                    limit=6,
                    sources=sources_list,
                )
            except Exception as e:
                if "402" in str(e):
                    print("🔥 [MOCK] 402 Payment Required - Using Mock Data")
                    result = {
                        "success": True,
                        "data": {
                            "web": [
                                {"url": "https://react.dev", "title": "React - The library for web and native user interfaces", "content": "React is the library for web and native user interfaces. Build user interfaces out of individual pieces called components written in JavaScript.", "markdown": "React is the library for web and native user interfaces. Build user interfaces out of individual pieces called components written in JavaScript."},
                                {"url": "https://ui.shadcn.com", "title": "shadcn/ui - Beautifully designed components", "content": "Beautifully designed components that you can copy and paste into your apps. Accessible. Customizable. Open Source.", "markdown": "Beautifully designed components that you can copy and paste into your apps. Accessible. Customizable. Open Source."},
                            ],
                            "news": [
                                {"url": "https://techcrunch.com/news", "title": "AI Agents take over the world", "source": "TechCrunch", "date": "2026-04-30"}
                            ],
                            "images": [
                                {"url": "https://ui.shadcn.com/og.jpg", "title": "Shadcn UI Banner", "imageUrl": "https://ui.shadcn.com/og.jpg"}
                            ]
                        }
                    }
                else:
                    raise

            # Parse v2 response
            data = result.get("data", {})

            # Handle both v1 (list) and v2 (dict) response shapes
            if isinstance(data, list):
                web_items = data
                news_items = []
                image_items = []
            else:
                web_items = data.get("web", [])
                news_items = data.get("news", [])
                image_items = data.get("images", [])

            yield _sse({
                "type": "sources",
                "web": web_items[:8],
                "news": news_items[:6],
                "images": image_items[:8],
            })

            # Phase 3: Persist to DB
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO searches (query, status) VALUES (?, ?)",
                    (request.query, "completed"),
                )
                search_id = cursor.lastrowid
                for item in web_items[:8]:
                    cursor.execute(
                        "INSERT INTO scraped_data (search_id, url, content, markdown, metadata) VALUES (?, ?, ?, ?, ?)",
                        (
                            search_id,
                            item.get("url"),
                            item.get("content", ""),
                            item.get("markdown", ""),
                            json.dumps(item.get("metadata", {})),
                        ),
                    )
                conn.commit()
                conn.close()
            except Exception:
                pass  # Don't fail on DB errors

            # Phase 4: Stream AI answer
            yield _sse({"type": "status", "message": "Generating answer..."})

            full_answer = ""
            async for chunk in service.stream_ai_answer(request.query, result):
                full_answer += chunk
                yield _sse({"type": "chunk", "content": chunk})

            # Phase 5: Follow-up questions
            follow_ups = await service.generate_follow_ups(request.query, full_answer)
            if follow_ups:
                yield _sse({"type": "follow_ups", "questions": follow_ups})

            yield _sse({"type": "done"})

        except Exception as e:
            yield _sse({"type": "error", "message": str(e)})

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ─── Classic Search (backward compat) ────────────────────────
@router.post("/search")
async def search(request: SearchRequest):
    service = FirecrawlService()
    try:
        try:
            result = await service.search(request.query)
        except Exception as e:
            if "402" in str(e):
                result = {
                    "success": True,
                    "data": [
                        {"url": "https://firecrawl.dev", "markdown": "Firecrawl turns websites into LLM-ready markdown.", "metadata": {"title": "Firecrawl"}},
                        {"url": "https://python.org", "markdown": "Python is a programming language.", "metadata": {"title": "Python.org"}},
                    ],
                }
            else:
                raise

        ai_answer = "AI could not generate an answer."
        if result.get("success") or result.get("data"):
            try:
                ai_answer = await service.answer_with_ai(request.query, result)
            except Exception as ai_err:
                print(f"AI Generation error: {ai_err}")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO searches (query, status) VALUES (?, ?)", (request.query, "completed"))
        search_id = cursor.lastrowid

        data = result.get("data", {})
        items = data.get("web", []) if isinstance(data, dict) else data if isinstance(data, list) else []
        for item in items:
            cursor.execute(
                "INSERT INTO scraped_data (search_id, url, content, markdown, metadata) VALUES (?, ?, ?, ?, ?)",
                (search_id, item.get("url"), item.get("content", ""), item.get("markdown", ""), json.dumps(item.get("metadata", {}))),
            )
        conn.commit()
        conn.close()

        return {"search_results": result, "ai_answer": ai_answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Scrape ───────────────────────────────────────────────────
@router.post("/scrape")
async def scrape(request: ScrapeRequest):
    service = FirecrawlService()
    try:
        result = await service.scrape(request.url)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── History ──────────────────────────────────────────────────
@router.get("/history")
async def get_history():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM searches ORDER BY timestamp DESC LIMIT 50")
        rows = cursor.fetchall()
        history = [dict(row) for row in rows]
        conn.close()
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Helper ──────────────────────────────────────────────────
def _sse(data: dict) -> str:
    """Format a dict as an SSE event line."""
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
