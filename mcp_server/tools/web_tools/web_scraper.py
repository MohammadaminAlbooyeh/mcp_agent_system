from mcp_server.tools.base_tool import BaseTool


class WebScraperTool(BaseTool):
    def __init__(self):
        super().__init__()
        self.name = "web_scraper"
        self.description = "Scrape content from a web page"
        self.input_schema = {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to scrape"},
                "selectors": {"type": "string", "description": "CSS selectors to extract"},
            },
            "required": ["url"],
        }

    async def execute(self, url: str, selectors: str = None) -> str:
        import httpx
        from bs4 import BeautifulSoup
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(response.text, "html.parser")
            if selectors:
                elements = soup.select(selectors)
                return "\n".join(el.get_text(strip=True) for el in elements)
            return soup.get_text(strip=True)[:3000]
