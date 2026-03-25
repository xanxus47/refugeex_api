from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import get_pool, close_pool
from routers import evacuee
import logging

# Setup basic logging to see errors in Railway "View Logs"
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info("Connecting to Supabase...")
        await get_pool()   # warm up connection pool on startup
        logger.info("Database connection successful! 🚀")
    except Exception as e:
        logger.error(f"Database connection failed on startup: {e}")
        # We don't 'raise' the error here so the server can still start
    yield
    await close_pool() # clean up on shutdown


app = FastAPI(
    title="Refugeex API",
    description="Evacuee management API for MDRRMO Magsaysay — powered by Supabase",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# FIXED: Removed the "/api/v1" prefix
app.include_router(evacuee.router) 


@app.get("/")
def root():
    return {"message": "Refugeex API is running 🏠", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}