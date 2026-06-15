# ============================================================
# session.py — Creates the connection to PostgreSQL
# ============================================================
# This file has TWO things:
#
# 1. ENGINE  — the actual connection to the database
#    Think of it like a phone line to PostgreSQL.
#    You create it ONCE, and reuse it everywhere.
#
# 2. SessionLocal — a "session factory"
#    A session = one conversation with the database.
#    You open a session → do queries → close it.
#    SessionLocal creates new sessions for you.
#
# 3. get_db() — a helper function for FastAPI
#    FastAPI calls this before each request to give
#    your route a database session, and closes it after.
#
# FLOW:
#   .env → config.py (reads URL) → THIS FILE (connects to DB)
#                                      ↓
#                                  main.py uses `engine` to test connection
#                                  routes will use `get_db()` to talk to DB
# ============================================================

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


# STEP 1: Create the engine (the connection)
engine = create_engine(
    settings.DATABASE_URL,   # ← the URL from .env via config.py
)

# STEP 2: Create a session factory
SessionLocal = sessionmaker(
    bind=engine,             # ← sessions use this engine (connection)
    autocommit=False,        # ← we manually control when to save (commit)
    autoflush=False          # ← we manually control when to send to DB
)


# STEP 3: Dependency function for FastAPI routes
def get_db():
    """
    Usage in a route:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            ...

    FastAPI will:
      1. Call get_db() → creates a new session
      2. Give it to your route as `db`
      3. After the route finishes → close the session
    """
    db = SessionLocal()
    try:
        yield db        # ← gives the session to the route
    finally:
        db.close()      # ← always closes, even if there's an error