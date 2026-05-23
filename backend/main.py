"""
H-Automate — main.py
FastAPI application entry point.

Run with:
    uvicorn main:app --reload --port 8000

API base: http://localhost:8000/api
Docs:     http://localhost:8000/docs
"""

import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from routes.analyst import router as analyst_router
from routes.operations import router as operations_router


# ─────────────────────────────────────────────
# RATE LIMITER
# 5 requests/minute per IP — prevents Groq quota
# burn when users tap Analyze repeatedly on slow
# Nigerian mobile connections.
# ─────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address, default_limits=["5/minute"])


# ─────────────────────────────────────────────
# STARTUP / SHUTDOWN
# ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Verify environment is ready before accepting requests."""
    if not os.getenv("GROQ_API_KEY"):
        raise RuntimeError(
            "GROQ_API_KEY not found. "
            "Create a .env file and add: GROQ_API_KEY=your_key_here"
        )
    print("[OK] H-Automate API ready")
    print(f"   Groq API key: {'*' * 20}{os.getenv('GROQ_API_KEY', '')[-4:]}")
    yield
    print("H-Automate API shutting down.")


# ─────────────────────────────────────────────
# APP INSTANCE
# ─────────────────────────────────────────────
app = FastAPI(
    title="H-Automate API",
    description="AI business operations assistant for Nigerian SMEs",
    version="1.0.0",
    lifespan=lifespan,
)

# Register rate limiter and its error handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# ─────────────────────────────────────────────
# CORS
# FIX 1: Wildcard "*" removed.
# Only explicitly listed origins are allowed.
# Add your production domain here before deploying.
# ─────────────────────────────────────────────
ALLOWED_ORIGINS = [
    "http://localhost:5173",          # Vite dev server
    "http://localhost:3000",          # Alternative dev port
    "https://h-automate.vercel.app",  # Production — update to your actual domain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────
# ROUTERS
# ─────────────────────────────────────────────
app.include_router(analyst_router,    prefix="/api", tags=["Business Insights"])
app.include_router(operations_router, prefix="/api", tags=["Smart Operations"])


# ─────────────────────────────────────────────
# STATIC FILES — sample data served to frontend
# Accessible at: GET /sample-data/minimart_sales.csv
# ─────────────────────────────────────────────
SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "sample_data")
if os.path.isdir(SAMPLE_DATA_DIR):
    app.mount(
        "/sample-data",
        StaticFiles(directory=SAMPLE_DATA_DIR),
        name="sample_data",
    )


# ─────────────────────────────────────────────
# HEALTH CHECK
# FIX 2: groq_key_loaded removed — no need to
# expose API key status to external callers.
# Startup log already confirms the key loaded.
# ─────────────────────────────────────────────
@app.get("/health", tags=["System"])
def health_check():
    """
    Returns API status. Frontend polls this on load.
    If this returns non-200, show the 'AI unavailable' error state.
    """
    return {
        "status":  "ok",
        "product": "H-Automate",
        "version": "1.0.0",
    }


@app.get("/", tags=["System"])
def root():
    return {
        "message": "H-Automate API is running",
        "docs":    "/docs",
        "health":  "/health",
        "endpoints": {
            "analyze":    "POST /api/analyze",
            "operations": "POST /api/operations",
        },
    }

# Made with Bob
