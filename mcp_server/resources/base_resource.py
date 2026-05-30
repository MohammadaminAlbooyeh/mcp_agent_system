from abc import ABC, abstractmethod
import mcp.types as types


class BaseResource(ABC):
    def __init__(self):
        self.uri: str = ""
        self.name: str = ""
        self.description: str = ""
        self.mime_type: str = "text/plain"

    @abstractmethod
    async def read(self) -> str:
        pass

    def to_mcp_resource(self) -> types.Resource:
        return types.Resource(
            uri=self.uri,
            name=self.name,
            description=self.description,
            mimeType=self.mime_type,
        )
