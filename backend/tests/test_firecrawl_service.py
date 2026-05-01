import os
import sys
import pytest
import httpx
from unittest.mock import AsyncMock, patch

# Add backend dir to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from common.firecrawl_service import FirecrawlService


def _make_response(status_code: int, json_data: dict) -> httpx.Response:
    """Helper to create a properly formed httpx.Response with a request set."""
    request = httpx.Request("POST", "https://api.firecrawl.dev/v2/test")
    response = httpx.Response(status_code, json=json_data, request=request)
    return response


@pytest.fixture
def firecrawl_service():
    with patch("common.firecrawl_service.FIRECRAWL_API_KEY", "test_key"), \
         patch("common.firecrawl_service.FREELLM_API_KEY", "test_llm_key"), \
         patch("common.firecrawl_service.FREELLM_BASE_URL", "http://localhost:3001/v1"), \
         patch("common.firecrawl_service.DEFAULT_MODEL", "gpt-4o"):
        return FirecrawlService()


async def test_search_success(firecrawl_service):
    mock_response = {
        "success": True,
        "data": {"web": [{"url": "https://example.com", "title": "Example", "markdown": "hello"}]}
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = _make_response(200, mock_response)

        result = await firecrawl_service.search("test query")

        assert result == mock_response
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert args[0] == "https://api.firecrawl.dev/v2/search"
        assert kwargs["json"]["query"] == "test query"
        assert kwargs["headers"]["Authorization"] == "Bearer test_key"


async def test_search_with_sources(firecrawl_service):
    """Test that sources parameter is passed through."""
    mock_response = {
        "success": True,
        "data": {"web": [], "news": [], "images": []}
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = _make_response(200, mock_response)

        result = await firecrawl_service.search("test", sources=["web", "news"])

        args, kwargs = mock_post.call_args
        assert kwargs["json"]["sources"] == ["web", "news"]


async def test_scrape_success(firecrawl_service):
    mock_response = {
        "success": True,
        "data": {"content": "scraped content"}
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = _make_response(200, mock_response)

        result = await firecrawl_service.scrape("https://example.com")

        assert result == mock_response
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert args[0] == "https://api.firecrawl.dev/v2/scrape"
        assert kwargs["headers"]["Authorization"] == "Bearer test_key"


async def test_api_error(firecrawl_service):
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = _make_response(401, {"error": "Unauthorized"})

        with pytest.raises(httpx.HTTPStatusError):
            await firecrawl_service.search("test query")


async def test_crawl(firecrawl_service):
    mock_response = {"success": True, "id": "job_123"}

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = _make_response(200, mock_response)

        result = await firecrawl_service.crawl("https://example.com", limit=10)

        assert result["id"] == "job_123"
        args, kwargs = mock_post.call_args
        assert args[0] == "https://api.firecrawl.dev/v2/crawl"
        assert kwargs["json"]["url"] == "https://example.com"
        assert kwargs["json"]["limit"] == 10
