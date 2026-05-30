from mcp_server.utils.logger import get_logger

logger = get_logger(__name__)


class ResourceHandler:
    def __init__(self, server):
        self.server = server

    async def handle_resource_request(self, uri: str) -> str:
        try:
            resource = self.server.get_resource(uri)
            logger.info(f"Reading resource: {uri}")
            return await resource.read()
        except Exception as e:
            logger.error(f"Error reading resource {uri}: {e}")
            return f"Error: {e}"
