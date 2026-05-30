from mcp_server.tools.base_tool import BaseTool


class DBWriterTool(BaseTool):
    def __init__(self):
        super().__init__()
        self.name = "db_writer"
        self.description = "Insert or update data in database tables"
        self.input_schema = {
            "type": "object",
            "properties": {
                "table": {"type": "string", "description": "Table name"},
                "data": {"type": "object", "description": "Column-value pairs to insert/update"},
                "mode": {"type": "string", "enum": ["insert", "update"], "description": "Insert or update"},
                "where": {"type": "string", "description": "WHERE clause for updates"},
            },
            "required": ["table", "data"],
        }

    async def execute(self, table: str, data: dict, mode: str = "insert", where: str = None) -> str:
        from backend.models.database import get_session
        session = get_session()
        try:
            if mode == "insert":
                cols = ", ".join(data.keys())
                vals = ", ".join(f":{k}" for k in data.keys())
                query = f"INSERT INTO {table} ({cols}) VALUES ({vals})"
            else:
                set_clause = ", ".join(f"{k} = :{k}" for k in data.keys())
                query = f"UPDATE {table} SET {set_clause}"
                if where:
                    query += f" WHERE {where}"
            session.execute(query, data)
            session.commit()
            return f"Successfully {mode}ed data into {table}"
        except Exception as e:
            return f"Error writing to database: {e}"
        finally:
            session.close()
