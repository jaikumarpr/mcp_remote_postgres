import sys
import logging
from fastmcp import FastMCP
from contextlib import asynccontextmanager
from tools import register_tools
from db import Database, initialize_database, cleanup_database

logger = logging.getLogger(__name__)

_db: Database = Database()

_db_url: str = ""

@asynccontextmanager
async def lifespan(app):

    global _db, _db_url

    try:
        logger.info("Initializing database...")
        await initialize_database(_db_url, _db)
        logger.info("Database connection established")
    except Exception as e:
        logger.error(f"Error setting up database: {e}")
        sys.exit(1)

    yield

    try:
        logger.info("Cleaning up resources...")
        await cleanup_database(_db)
        logger.info("Database pool closed successfully")
    except Exception as e:
        logger.error(f"Error cleaning up database: {e}")
        
        
def setup(db_url: str) -> FastMCP:
    
    global _db, _db_url

    _db_url = db_url
    
    try:
        mcp = FastMCP(name="remote-postgres-mcp",
                      instructions="""
                        This server provides tools to perform read-only operations on a PostgreSQL database.
                        Use execute_query to execute SELECT statements and retrieve data.
                        Use get_table_schema to understand table structures.
                        Always be careful with destructive operations.""",
                      lifespan=lifespan)

        register_tools(mcp, _db)

        return mcp

    except Exception as e:
        raise Exception(f"Error setting up MCP: {e}")
        
def run(mcp: FastMCP, **kwargs) -> None:

    try:
        mcp.run(**kwargs)
        logger.info("Starting Remote Postgres MCP server...")
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        logger.info("Server stopped")
