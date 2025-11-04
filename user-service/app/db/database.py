"""
Database configuration and session management for the User Management Service.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# ----------------------------------------------------------------------
# Database Engine Setup
# ----------------------------------------------------------------------

# Example: postgresql://user_admin:user_pass@user-db:5432/user_db
DATABASE_URL = settings.DATABASE_URL

# Create SQLAlchemy engine
# pool_pre_ping=True → checks connections before using them
# future=True → ensures SQLAlchemy 2.x API behavior
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=False,  # Set True if you want SQL logs for debugging
    future=True
)

# ----------------------------------------------------------------------
# Session Factory
# ----------------------------------------------------------------------

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)

# ----------------------------------------------------------------------
# Base Model Class
# ----------------------------------------------------------------------

Base = declarative_base()

# ----------------------------------------------------------------------
# Dependency Helper
# ----------------------------------------------------------------------

def get_db():
    """
    FastAPI dependency that provides a SQLAlchemy session.
    It automatically closes after the request is complete.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
