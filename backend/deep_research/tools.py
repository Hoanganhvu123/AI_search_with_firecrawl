import httpx
from langchain_core.tools import tool

@tool
async def web_search(query: str) -> str:
    """Search the web to discover relevant pages. Returns raw search results."""
    async with httpx.AsyncClient() as client:
        headers = {"Accept": "application/json"}
        try:
            response = await client.get(f"https://s.jina.ai/{query}", headers=headers, timeout=30.0)
            if response.status_code == 200:
                data = response.json()
                results = []
                for item in data.get("data", [])[:5]:
                    results.append(f"Title: {item.get('title')}\nURL: {item.get('url')}\nSnippet: {item.get('description')}\n")
                return "\n".join(results) if results else "No results found."
            return f"Search failed with status {response.status_code}"
        except Exception as e:
            return f"Error during search: {str(e)}"

@tool
async def scrape_url(url: str) -> str:
    """Extract content from a URL. Returns markdown content of the page."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"https://r.jina.ai/{url}", timeout=30.0)
            if response.status_code == 200:
                return response.text[:15000] # Limit to 15k chars to avoid massive context
            return f"Scrape failed with status {response.status_code}"
        except Exception as e:
            return f"Error during scrape: {str(e)}"

@tool
def format_output(format: str, data: str) -> str:
    """Export results as JSON or markdown text. Call this when you have collected enough data to answer the prompt."""
    return data

DEEP_RESEARCH_TOOLS = [web_search, scrape_url, format_output]
