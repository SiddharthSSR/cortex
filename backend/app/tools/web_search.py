"""Web search tool for searching the internet."""

import logging
from typing import Dict
import httpx
from bs4 import BeautifulSoup

from app.tools.base_tool import BaseTool, ToolParameter, ToolResult

logger = logging.getLogger(__name__)


class WebSearchTool(BaseTool):
    """Tool for searching the web."""

    def __init__(self, api_key: str = None):
        """Initialize web search tool.

        Args:
            api_key: Optional API key for search service (e.g., Serper, SerpAPI)
        """
        super().__init__()
        self.api_key = api_key

    @property
    def name(self) -> str:
        return "web_search"

    @property
    def description(self) -> str:
        return (
            "Searches the web for information about a given query. "
            "Returns search results including titles, URLs, and snippets. "
            "Useful for finding current information, facts, news, or any web content. "
            "Example queries: 'latest news on AI', 'weather in San Francisco', "
            "'Python programming tutorial'"
        )

    @property
    def parameters(self) -> Dict[str, ToolParameter]:
        return {
            "query": ToolParameter(
                type="string",
                description="The search query to look up on the web",
                required=True,
            ),
            "num_results": ToolParameter(
                type="integer",
                description="Number of search results to return (default: 5)",
                required=False,
                default=5,
            ),
        }

    async def execute(self, query: str, num_results: int = 5) -> ToolResult:
        """Execute web search.

        Args:
            query: Search query string
            num_results: Number of results to return

        Returns:
            ToolResult with search results or error
        """
        if not query or not query.strip():
            return ToolResult(success=False, error="Search query cannot be empty")

        # Limit results to reasonable number
        num_results = min(max(1, num_results), 10)

        try:
            # Use DuckDuckGo HTML search (no API key needed)
            results = await self._duckduckgo_search(query, num_results)

            if not results:
                return ToolResult(
                    success=False,
                    error="No search results found",
                    metadata={"query": query},
                )

            # Format results
            formatted_results = []
            for i, result in enumerate(results, 1):
                formatted_results.append(
                    f"{i}. {result['title']}\n"
                    f"   URL: {result['url']}\n"
                    f"   {result['snippet']}"
                )

            result_text = "\n\n".join(formatted_results)

            logger.info(f"Web search for '{query}' returned {len(results)} results")

            return ToolResult(
                success=True,
                result=result_text,
                metadata={
                    "query": query,
                    "num_results": len(results),
                    "results": results,
                },
            )

        except Exception as e:
            error_msg = f"Web search failed: {str(e)}"
            logger.error(error_msg)
            return ToolResult(success=False, error=error_msg)

    async def _duckduckgo_search(self, query: str, num_results: int) -> list:
        """Perform DuckDuckGo search via HTML scraping.

        Args:
            query: Search query
            num_results: Number of results to fetch

        Returns:
            List of search result dictionaries
        """
        try:
            url = "https://html.duckduckgo.com/html/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            }

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    url, data={"q": query}, headers=headers, follow_redirects=True
                )
                response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            results = []

            # Parse search results
            for result_div in soup.find_all("div", class_="result"):
                if len(results) >= num_results:
                    break

                # Extract title and URL
                title_elem = result_div.find("a", class_="result__a")
                if not title_elem:
                    continue

                title = title_elem.get_text(strip=True)
                url = title_elem.get("href", "")

                # Extract snippet
                snippet_elem = result_div.find("a", class_="result__snippet")
                snippet = (
                    snippet_elem.get_text(strip=True) if snippet_elem else "No description"
                )

                if title and url:
                    results.append({"title": title, "url": url, "snippet": snippet})

            return results

        except httpx.HTTPError as e:
            logger.error(f"HTTP error during DuckDuckGo search: {e}")
            raise Exception(f"Search request failed: {str(e)}")
        except Exception as e:
            logger.error(f"Error parsing DuckDuckGo results: {e}")
            raise Exception(f"Failed to parse search results: {str(e)}")
