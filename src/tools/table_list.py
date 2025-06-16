from typing import Annotated, Any, Dict
from pydantic import Field
from fastmcp import Context
from db import Database


def list_tables_tool(db: Database):
    async def list_tables(
        schema_name: Annotated[str, Field(default="public", description="Schema name to list tables from")] = "public",
        ctx: Context = None
    ) -> Dict[str, Any]:
        """
        List all tables in the specified schema.
        """
        if ctx:
            await ctx.info(f"Listing tables in schema: {schema_name}")
        
        query = """
        SELECT table_name, table_type
        FROM information_schema.tables 
        WHERE table_schema = $1
        ORDER BY table_name;
        """
        
        try:
            async with db.get_connection() as connection:   
                async with connection.transaction(readonly=True):
                    rows = await connection.fetch(query, schema_name)
                
                    tables = [{"name": row['table_name'], "type": row['table_type']} for row in rows]
                    
                    if ctx:
                        await ctx.info(f"Found {len(tables)} tables")
                    
                    return {
                        "success": True,
                        "schema_name": schema_name,
                        "tables": tables
                    }
        
        except Exception as e:
            if ctx:
                await ctx.error(f"Failed to list tables: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "tables": []
            }
            
    return list_tables