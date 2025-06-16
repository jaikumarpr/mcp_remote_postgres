from typing import Annotated, Any, Dict
from pydantic import Field
from fastmcp import Context
from db import Database


def get_table_schema_tool(db: Database):
    async def get_table_schema(
        table_name: Annotated[str, Field(description="Name of the table to describe")],
        schema_name: Annotated[str, Field(default="public", description="Schema name (default: public)")] = "public",
        ctx: Context = None
    ) -> Dict[str, Any]:
        """
        Get the schema information for a specific table including columns, types, and constraints.
        """
        if ctx:
            await ctx.info(f"Getting schema for table: {schema_name}.{table_name}")
        
        query = """
        WITH column_info AS (
            SELECT 
                c.column_name,
                c.data_type,
                c.is_nullable,
                c.column_default,
                c.character_maximum_length,
                c.numeric_precision,
                c.numeric_scale,
                c.ordinal_position,
                CASE 
                    WHEN c.data_type = 'USER-DEFINED' THEN c.udt_name
                    ELSE c.data_type 
                END as full_data_type
            FROM information_schema.columns c
            WHERE c.table_schema = $1 AND c.table_name = $2
        ),
        primary_keys AS (
            SELECT kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu 
                ON tc.constraint_name = kcu.constraint_name
            WHERE tc.table_schema = $1 
                AND tc.table_name = $2
                AND tc.constraint_type = 'PRIMARY KEY'
        ),
        foreign_keys AS (
            SELECT 
                kcu.column_name,
                ccu.table_schema as foreign_table_schema,
                ccu.table_name as foreign_table_name,
                ccu.column_name as foreign_column_name,
                tc.constraint_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu 
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage ccu 
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.table_schema = $1 
                AND tc.table_name = $2
                AND tc.constraint_type = 'FOREIGN KEY'
        ),
        unique_constraints AS (
            SELECT kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu 
                ON tc.constraint_name = kcu.constraint_name
            WHERE tc.table_schema = $1 
                AND tc.table_name = $2
                AND tc.constraint_type = 'UNIQUE'
        )
        SELECT 
            ci.column_name,
            ci.full_data_type,
            ci.is_nullable,
            ci.column_default,
            ci.character_maximum_length,
            ci.numeric_precision,
            ci.numeric_scale,
            ci.ordinal_position,
            CASE WHEN pk.column_name IS NOT NULL THEN true ELSE false END as is_primary_key,
            CASE WHEN fk.column_name IS NOT NULL THEN true ELSE false END as is_foreign_key,
            CASE WHEN uc.column_name IS NOT NULL THEN true ELSE false END as is_unique,
            fk.foreign_table_schema,
            fk.foreign_table_name,
            fk.foreign_column_name,
            fk.constraint_name as fk_constraint_name
        FROM column_info ci
        LEFT JOIN primary_keys pk ON ci.column_name = pk.column_name
        LEFT JOIN foreign_keys fk ON ci.column_name = fk.column_name
        LEFT JOIN unique_constraints uc ON ci.column_name = uc.column_name
        ORDER BY ci.ordinal_position;
        """
        
        try:
            async with db.get_connection() as connection:
                async with connection.transaction(readonly=True):
                    rows = await connection.fetch(query, schema_name, table_name)
                
                    if not rows:
                        return {
                            "success": False,
                            "error": f"Table {schema_name}.{table_name} not found",
                            "schema": []
                        }
                
                    schema_info = []
                    for row in rows:
                        column_info = {
                            "column_name": row['column_name'],
                            "data_type": row['full_data_type'],
                            "is_nullable": row['is_nullable'] == 'YES',
                            "column_default": row['column_default'],
                            "ordinal_position": row['ordinal_position'],
                            "is_primary_key": row['is_primary_key'],
                            "is_foreign_key": row['is_foreign_key'],
                            "is_unique": row['is_unique']
                        }
                        
                        # Add length info for character types
                        if row['character_maximum_length']:
                            column_info["max_length"] = row['character_maximum_length']
                        
                        # Add precision/scale for numeric types
                        if row['numeric_precision']:
                            column_info["precision"] = row['numeric_precision']
                        if row['numeric_scale']:
                            column_info["scale"] = row['numeric_scale']
                        
                        # Add foreign key relationship info
                        if row['is_foreign_key']:
                            column_info["foreign_key"] = {
                                "table_schema": row['foreign_table_schema'],
                                "table_name": row['foreign_table_name'],
                                "column_name": row['foreign_column_name'],
                                "constraint_name": row['fk_constraint_name']
                            }
                        
                        schema_info.append(column_info)
                
                    if ctx:
                        await ctx.info(f"Retrieved schema for {len(schema_info)} columns")
                    
                    return {
                        "success": True,
                        "table_name": table_name,
                        "schema_name": schema_name,
                        "columns": schema_info
                    }
        
        except Exception as e:
            if ctx:
                await ctx.error(f"Failed to get schema: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "schema": []
            }
            
    return get_table_schema