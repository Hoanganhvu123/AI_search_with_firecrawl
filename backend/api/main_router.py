from fastapi import APIRouter
from api.fire_api import router as fire_router

# -------------------------------------------------------------------------
# Main API Router — Firecrawl Only
# -------------------------------------------------------------------------
api_router = APIRouter()

api_router.include_router(fire_router, prefix="/firecrawl", tags=["firecrawl"])
