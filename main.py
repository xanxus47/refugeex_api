from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import get_pool, close_pool
from routers import evacuee
import logging

# Setup logging to see connection status in Railway Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info("Connecting to Supabase via Pooler...")
        await get_pool()
        logger.info("Database connection successful! 🏠")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
    yield
    await close_pool()

app = FastAPI(
    title="Refugeex API",
    description="Evacuee management API for MDRRMO Magsaysay",
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

# Prefix removed as requested!
app.include_router(evacuee.router) 

@app.get("/")
def root():
    return {"message": "Refugeex API is running 🏠", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "ok"}