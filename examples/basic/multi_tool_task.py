import asyncio
from mcp_server.tools.web_tools.web_search import WebSearchTool
from mcp_server.tools.utility_tools.text_processor import TextProcessorTool


async def main():
    search = WebSearchTool()
    search_result = await search.execute(query="Python programming", num_results=3)
    print("Search Results:", search_result[:500])

    processor = TextProcessorTool()
    processed = await processor.execute(text=search_result, operation="count_words")
    print(processed)


if __name__ == "__main__":
    asyncio.run(main())
