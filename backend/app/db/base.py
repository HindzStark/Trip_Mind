# ============================================================
# base.py — The "parent class" for all your database tables
# ============================================================
# WHAT IS THIS?
#   In SQLAlchemy, every table you create is a Python class.
#   All those classes must inherit from one common Base class.
#   This file creates that Base class.
#
# ANALOGY:
#   Think of Base like a blank form template.
#   Every specific form (User, Trip, Hotel) is made FROM this template.
#
# EXAMPLE (you'll do this later):
#   from app.db.base import Base
#
#   class User(Base):              ← inherits from Base
#       __tablename__ = "users"    ← this becomes the table name in PostgreSQL
#       id = ...
#       email = ...
# ============================================================

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass