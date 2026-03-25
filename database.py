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
            min_size=5,    # Keep 5 connections ready at all times
            max_size=50,   # Allow up to 50 simultaneous database tasks
            ssl="require",
            # Add these to prevent "hanging" connections
            command_timeout=60,
            max_inactive_connection_lifetime=300 
        )
    return _pool


async def close_pool():
    global _pool
    if _pool:
        await _pool.close()
        _pool = None
