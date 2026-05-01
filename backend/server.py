import asyncio
import logging
import os
import platform

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from api.main_router import api_router
from config import PORT


if platform.system() == "Windows":
    print("[WINDOWS] Applying SelectorEventLoopPolicy globally...")
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)

# Static files directory
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)
print(f"[OK] Static dir resolved: {STATIC_DIR}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize Firecrawl Search Database on startup."""
    from database.fire_db import init_db
    init_db()
    logger.info("[OK] Firecrawl Search Database initialized")

    yield

    logger.info("[STOP] Server shutting down")


app = FastAPI(
    title="Firecrawl AI Search",
    description="AI-powered web search using Firecrawl + LLM",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
async def root():
    return RedirectResponse(url="/firecrawl/ui/index.html")

@app.get("/health")
async def health():
    return JSONResponse({"status": "ok"})


# =====================================================================
# CORS
# =====================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# API routes
app.include_router(api_router)

# Mount Firecrawl Dashboard
FIRE_SEARCH_STATIC = os.path.join(STATIC_DIR, "fire_search")
if os.path.exists(FIRE_SEARCH_STATIC):
    app.mount("/firecrawl/ui", StaticFiles(directory=FIRE_SEARCH_STATIC), name="firecrawl_ui")
    print(f"[OK] Firecrawl UI mounted at: /firecrawl/ui")


if __name__ == "__main__":
    print("=" * 60)
    print("[FIRE] Firecrawl AI Search Starting...")
    print("=" * 60)
    print(f"[API]  REST API:      http://localhost:{PORT}")
    print(f"[DOC]  API Docs:      http://localhost:{PORT}/docs")
    print(f"[UI]   Search UI:     http://localhost:{PORT}/firecrawl/ui/index.html")
    print("=" * 60)

    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=PORT,
        reload=False,
        log_level="info",
    )
