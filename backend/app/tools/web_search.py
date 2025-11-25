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
        """Perform DuckDuckGo search using different methods.

        Args:
            query: Search query
            num_results: Number of results to fetch

        Returns:
            List of search result dictionaries
        """
        try:
            # Use GET request to main search page (more reliable)
            import urllib.parse
            encoded_query = urllib.parse.quote_plus(query)
            url = f"https://duckduckgo.com/html/?q={encoded_query}"

            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/121.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Cache-Control": "max-age=0",
            }

            async with httpx.AsyncClient(
                timeout=20.0,
                follow_redirects=True,
                http2=True,
            ) as client:
                logger.info(f"Fetching search results from: {url}")
                response = await client.get(url, headers=headers)

                logger.info(f"DuckDuckGo response status: {response.status_code}")
                logger.info(f"Response content length: {len(response.text)}")

                if response.status_code != 200:
                    logger.error(f"Non-200 status code: {response.status_code}")
                    raise Exception(f"DuckDuckGo returned status {response.status_code}")

            soup = BeautifulSoup(response.text, "html.parser")
            results = []

            # Method 1: Try standard result class
            result_divs = soup.find_all("div", class_="results_links")
            logger.info(f"Found {len(result_divs)} result divs with class 'results_links'")

            for result_div in result_divs:
                if len(results) >= num_results:
                    break

                # Try to find title link
                title_link = result_div.find("a", class_="result__a")
                if not title_link:
                    # Alternative: look for any link in result__title
                    title_container = result_div.find("h2", class_="result__title")
                    if title_container:
                        title_link = title_container.find("a")

                if title_link:
                    title = title_link.get_text(strip=True)
                    url_value = title_link.get("href", "")

                    # Find snippet
                    snippet = "No description available"
                    snippet_elem = result_div.find("a", class_="result__snippet")
                    if snippet_elem:
                        snippet = snippet_elem.get_text(strip=True)
                    else:
                        # Try alternative snippet location
                        desc_elem = result_div.find("div", class_="result__snippet")
                        if desc_elem:
                            snippet = desc_elem.get_text(strip=True)

                    if title and url_value:
                        results.append({
                            "title": title,
                            "url": url_value,
                            "snippet": snippet
                        })
                        logger.info(f"Extracted result: {title[:50]}...")

            # Method 2: If no results, try alternative structure
            if not results:
                logger.info("Trying alternative parsing method")
                all_result_divs = soup.find_all("div", class_="result")
                logger.info(f"Found {len(all_result_divs)} divs with class 'result'")

                for result_div in all_result_divs[:num_results]:
                    links = result_div.find_all("a", class_="result__a")
                    if links:
                        title = links[0].get_text(strip=True)
                        url_value = links[0].get("href", "")

                        snippet = "No description available"
                        snippet_elem = result_div.find("a", class_="result__snippet")
                        if snippet_elem:
                            snippet = snippet_elem.get_text(strip=True)

                        if title and url_value:
                            results.append({
                                "title": title,
                                "url": url_value,
                                "snippet": snippet
                            })

            logger.info(f"Successfully parsed {len(results)} search results")

            if not results:
                logger.warning("No results found - HTML structure may have changed")
                # Save HTML for debugging
                logger.debug(f"HTML content preview: {response.text[:500]}")

            return results

        except httpx.HTTPError as e:
            logger.error(f"HTTP error during DuckDuckGo search: {e}")
            raise Exception(f"Search request failed: {str(e)}")
        except Exception as e:
            logger.error(f"Error during DuckDuckGo search: {e}")
            raise Exception(f"Failed to parse search results: {str(e)}")
