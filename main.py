from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import get_pool, close_pool
from routers.evacuees import router as evacuee_router
import logging

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

app.include_router(evacuee_router)

@app.get("/")
def root():
    return {"message": "Refugeex API is running, Goodluck to all and take care always. Godspeed -Argie 😎"}

@app.get("/health")
def health():
    return {"status": "ok"}