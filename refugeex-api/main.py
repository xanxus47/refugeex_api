from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import get_pool, close_pool
from routers import evacuee


@asynccontextmanager
async def lifespan(app: FastAPI):
    await get_pool()   # warm up connection pool on startup
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
    allow_origins=["*"],  # restrict to your SvelteKit domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(evacuee.router, prefix="/api/v1")


@app.get("/")
def root():
    return {"message": "Refugeex API is running 🏠", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}
