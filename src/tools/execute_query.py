from typing import Annotated, List, Any, Dict
from pydantic import Field
from fastmcp import Context
from db import Database


def execute_query_tool(db: Database):
    async def execute_query(
        query: Annotated[str, Field(description="SQL SELECT query to execute")],
        params: Annotated[List[Any], Field(default=[], description="Query parameters for prepared statements")] = [],
        ctx: Context = None
    ) -> Dict[str, Any]:
        """
        Execute a SELECT query and return results.
        Use this for data retrieval operations only.
        """
        if ctx:
            await ctx.info(f"Executing query: {query[:100]}...")
        

        query_upper = query.strip().upper()
        if not query_upper.startswith('SELECT'):
            raise ValueError("This tool only supports SELECT queries. Use execute_command for other operations.")
        
        try:
            async with db.get_connection() as connection:

                async with connection.transaction(readonly=True):
                    rows = await connection.fetch(query, *params)
                    
                    results = [dict(row) for row in rows]
                    
                    if ctx:
                        await ctx.info(f"Query returned {len(results)} rows")
                    
                    return {
                        "success": True,
                        "row_count": len(results),
                        "data": results
                    }
        
        except Exception as e:
            if ctx:
                await ctx.error(f"Query failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "data": []
            }
    
    return execute_query