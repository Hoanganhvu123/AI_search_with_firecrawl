import os
import sys
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock

# Add backend dir to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from server import app

client = TestClient(app)

@pytest.fixture
def mock_firecrawl_service():
    with patch("api.fire_api.FirecrawlService") as mock:
        yield mock

@pytest.fixture
def mock_db_connection():
    with patch("api.fire_api.get_db_connection") as mock:
        mock_conn = MagicMock()
        mock.return_value = mock_conn
        yield mock_conn

def test_search_endpoint(mock_firecrawl_service, mock_db_connection):
    # Setup mock response for firecrawl service
    mock_service_instance = mock_firecrawl_service.return_value
    mock_service_instance.search = AsyncMock(return_value={
        "success": True, 
        "data": [{"url": "https://test.com", "markdown": "content"}]
    })
    mock_service_instance.answer_with_ai = AsyncMock(return_value="AI answer here")

    response = client.post("/firecrawl/search", json={"query": "test query"})
    
    assert response.status_code == 200
    data = response.json()
    assert "search_results" in data
    assert "ai_answer" in data

def test_scrape_endpoint(mock_firecrawl_service):
    mock_service_instance = mock_firecrawl_service.return_value
    mock_service_instance.scrape = AsyncMock(return_value={
        "success": True, 
        "data": {"content": "scraped"}
    })

    response = client.post("/firecrawl/scrape", json={"url": "https://test.com"})
    
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert mock_service_instance.scrape.called

def test_history_endpoint(mock_db_connection):
    mock_cursor = mock_db_connection.cursor.return_value
    mock_cursor.fetchall.return_value = [
        {"id": 1, "query": "test 1", "timestamp": "2023-01-01", "status": "success"},
        {"id": 2, "query": "test 2", "timestamp": "2023-01-02", "status": "success"}
    ]

    response = client.get("/firecrawl/history")
    
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["query"] == "test 1"
