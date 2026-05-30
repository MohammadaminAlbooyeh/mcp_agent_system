from mcp_server.resources.base_resource import BaseResource


class DatabaseResource(BaseResource):
    def __init__(self):
        super().__init__()
        self.uri = "database://schema"
        self.name = "Database Schema"
        self.description = "Current database schema information"

    async def read(self) -> str:
        try:
            from backend.models.database import get_session
            session = get_session()
            result = session.execute(
                "SELECT table_name, column_name, data_type "
                "FROM information_schema.columns "
                "WHERE table_schema = 'public' "
                "ORDER BY table_name, ordinal_position"
            )
            rows = result.fetchall()
            schema = {}
            for row in rows:
                table = row[0]
                if table not in schema:
                    schema[table] = []
                schema[table].append(f"{row[1]} ({row[2]})")
            output = []
            for table, cols in schema.items():
                output.append(f"\n{table}:")
                for col in cols:
                    output.append(f"  - {col}")
            return "\n".join(output)
        except Exception as e:
            return f"Database schema unavailable: {e}"
