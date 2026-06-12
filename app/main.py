# ============================================================
# main.py — Entry point of TripMind
# ============================================================
#
# FLOW:
#   .env → config.py → session.py → THIS FILE → starts server
#
# This file does 3 things:
#   1. Tests database connection on startup
#   2. Creates tables in PostgreSQL (from your models)
#   3. Registers all route files (so FastAPI knows about /trips, etc.)
# ============================================================

from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.db.session import engine
from app.db.base import Base

# This import makes SQLAlchemy aware of all your models.
# Without it, Base.metadata.create_all() won't create any tables.
import app.models  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: verify DB + create tables. Shutdown: dispose pool."""
    # --- STARTUP ---
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("Database connection successful!")
    except Exception as e:
        print(f"Database connection failed: {e}")
        raise

    # Create any tables that don't exist yet
    # In production, you'd use Alembic migrations instead
    Base.metadata.create_all(bind=engine)
    print("Database tables ready!")

    yield

    # --- SHUTDOWN ---
    engine.dispose()


app = FastAPI(
    title="TripMind",
    lifespan=lifespan,
)

# ---- REGISTER ROUTES ----
# app.include_router() tells FastAPI:
#   "Hey, there are more routes in this file — add them to the app."
#
# This is how APIRouter (in routes/trip.py) connects to the main app.

from app.routes.trip import router as trip_router

app.include_router(trip_router)

from app.routes.user import router as user_router
app.include_router(user_router)


@app.get("/")
def root():
    return {"message": "TripMind API Running"}