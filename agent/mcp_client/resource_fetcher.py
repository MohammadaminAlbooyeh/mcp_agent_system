from agent.utils.logger import get_logger

logger = get_logger(__name__)


class ResourceFetcher:
    def __init__(self, client):
        self.client = client

    async def fetch(self, uri: str) -> str:
        logger.info(f"Fetching resource: {uri}")
        try:
            result = await self.client.get_resource(uri)
            return result
        except Exception as e:
            logger.error(f"Resource fetch failed: {e}")
            return f"Resource fetch error: {e}"

    async def fetch_multiple(self, uris: list[str]) -> dict[str, str]:
        results = {}
        for uri in uris:
            results[uri] = await self.fetch(uri)
        return results
