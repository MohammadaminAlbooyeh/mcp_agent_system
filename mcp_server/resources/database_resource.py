from sqlalchemy import inspect
from mcp_server.resources.base_resource import BaseResource


class DatabaseResource(BaseResource):
    def __init__(self):
        super().__init__()
        self.uri = "database://schema"
        self.name = "Database Schema"
        self.description = "Current database schema information"

    async def read(self) -> str:
        try:
            from backend.models.database import engine
            inspector = inspect(engine)
            table_names = inspector.get_table_names()
            output = []
            for table_name in table_names:
                output.append(f"\n{table_name}:")
                columns = inspector.get_columns(table_name)
                for col in columns:
                    col_type = str(col["type"])
                    nullable = "NULL" if col["nullable"] else "NOT NULL"
                    pk = "PK" if col.get("primary_key") else ""
                    output.append(f"  - {col['name']} ({col_type}) {nullable} {pk}".strip())
            return "\n".join(output) if output else "No tables found in database."
        except Exception as e:
            return f"Database schema unavailable: {e}"
