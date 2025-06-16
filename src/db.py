import asyncpg
from typing import Optional

class Database:

    _instance: Optional['Database'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):

        if not hasattr(self, 'initialized'):
            self.pool: Optional[asyncpg.Pool] = None
            self.initialized = True
    
    async def create_pool(self, db_url: str, options: dict = {}):

        self.pool = await asyncpg.create_pool(
            db_url,
            **options
        )
    async def close_pool(self):
        if self.pool:
            await self.pool.close()
    
    def get_connection(self):
        if not self.pool:
            raise Exception("Database pool not initialized")
        return self.pool.acquire()
    
    def get_connection_pool(self):
        if not self.pool:
            raise Exception("Database pool not initialized")
        return self.pool
    
    async def execute_query(self, query: str, params: list = []) -> str:
        if not self.pool:
            raise Exception("Database pool not initialized")
        return await self.pool.fetch(query, *params)
    

async def initialize_database(db_url: str, db: Database):

    if not db_url:
        raise ValueError("DATABASE_URL is not set")

    try:
        await db.create_pool(db_url, {"min_size": 1, "max_size": 10, "command_timeout": 60})
    except Exception as e:
        raise Exception(f"Failed to initialize database: {str(e)}")


async def cleanup_database(db: Database):
    try:
        await db.close_pool()
    except Exception as e:
        raise Exception(str(e))