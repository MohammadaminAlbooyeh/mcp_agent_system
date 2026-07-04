from mcp_server.tools.base_tool import BaseTool
from mcp_server.tools.web_tools.search_parser import GoogleSearchParser, SearchResultFilter
from mcp_server.tools.web_tools.search_cache import InMemorySearchCache
from agent.utils.logger import get_logger
import json

logger = get_logger(__name__)


class WebSearchTool(BaseTool):
    def __init__(self):
        super().__init__()
        self.name = "web_search"
        self.description = "Search the web using Google and return structured results"
        self.input_schema = {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "num_results": {"type": "integer", "description": "Number of results (default: 10)"},
                "result_format": {
                    "type": "string",
                    "description": "Result format: 'structured' (default), 'text', or 'json'",
                    "enum": ["structured", "text", "json"]
                },
            },
            "required": ["query"],
        }
        self.cache = InMemorySearchCache(ttl_hours=24, max_size=500)
        self.parser = GoogleSearchParser()
        self.filter = SearchResultFilter()

    async def execute(self, query: str, num_results: int = 10, result_format: str = "structured") -> str:
        try:
            num_results = min(num_results, 20)

            cached_results = await self.cache.get(query, num_results)
            if cached_results:
                logger.debug(f"Cache hit for query: {query}")
                results = cached_results
            else:
                logger.debug(f"Searching: {query}")
                results = await self._search_google(query, num_results)

                if results and results.results:
                    await self.cache.put(query, num_results, results)

            if not results or not results.results:
                return f"No results found for query: {query}"

            results.results = self.filter.deduplicate(results.results)
            results.results = self.filter.filter_out_ads_and_duplicates(results.results)
            results.results = self.filter.rank_by_relevance(results.results, query)
            results.results = results.results[:num_results]

            if result_format == "json":
                return json.dumps({
                    "query": results.query,
                    "num_results": len(results.results),
                    "results": [
                        {
                            "position": r.position,
                            "title": r.title,
                            "url": r.url,
                            "snippet": r.snippet,
                            "domain": r.domain,
                        }
                        for r in results.results
                    ],
                }, indent=2)

            elif result_format == "text":
                output = f"Search results for '{query}' ({len(results.results)} results):\n\n"
                for result in results.results:
                    output += f"{result.position}. {result.title}\n"
                    output += f"   URL: {result.url}\n"
                    output += f"   {result.snippet}\n\n"
                return output

            else:  # structured
                return json.dumps({
                    "search": query,
                    "count": len(results.results),
                    "results": [
                        {
                            "position": r.position,
                            "title": r.title,
                            "url": r.url,
                            "domain": r.domain,
                            "snippet": r.snippet[:200],
                        }
                        for r in results.results
                    ],
                }, indent=2)

        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return f"Search failed: {str(e)}"

    async def _search_google(self, query: str, num_results: int):
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://www.google.com/search",
                    params={"q": query, "num": num_results},
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    },
                    timeout=10.0,
                )

                if response.status_code == 200:
                    results = self.parser.parse(response.text, query)
                    logger.debug(f"Found {len(results.results)} results")
                    return results

                logger.warning(f"Search returned status {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Failed to search Google: {e}")
            return None
