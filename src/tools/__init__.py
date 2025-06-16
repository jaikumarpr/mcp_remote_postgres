from .execute_query import execute_query_tool
from .get_table_schema import get_table_schema_tool
from .table_list import list_tables_tool
from fastmcp import FastMCP
from db import Database

def register_tools(mcp: FastMCP, db: Database):
    mcp.tool(execute_query_tool(db))
    mcp.tool(get_table_schema_tool(db))
    mcp.tool(list_tables_tool(db))


__all__ = ["register_tools"]

