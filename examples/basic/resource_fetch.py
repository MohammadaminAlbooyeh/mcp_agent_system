import asyncio
from mcp_server.resources.database_resource import DatabaseResource
from mcp_server.resources.api_resource import APIResource


async def main():
    db_resource = DatabaseResource()
    schema = await db_resource.read()
    print("Database Schema:", schema[:500])

    api_resource = APIResource()
    endpoints = await api_resource.read()
    print("\nAPI Endpoints:", endpoints)


if __name__ == "__main__":
    asyncio.run(main())
