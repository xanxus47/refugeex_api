import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

_pool: asyncpg.Pool = None


async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        # Render will provide this, locally it comes from .env
        database_url = os.getenv("DATABASE_URL")
        
        if not database_url:
            # Tip: Print a message to help you debug in the Render logs
            print("CRITICAL: DATABASE_URL is missing from environment variables!")
            raise RuntimeError("DATABASE_URL environment variable is not set")
            
        _pool = await asyncpg.create_pool(
            dsn=database_url,
            min_size=1,
            max_size=10,
            ssl="require", 
        )
    return _pool


async def close_pool():
    global _pool
    if _pool:
        await _pool.close()
        _pool = None
