import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

logger = logging.getLogger("archmind.database")

Base = declarative_base()

def get_engine():
    db_url = settings.DATABASE_URL
    connect_args = {}
    if db_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
        return create_engine(db_url, connect_args=connect_args)
    else:
        try:
            return create_engine(db_url, pool_pre_ping=True)
        except Exception as e:
            logger.warning(f"Could not initialize PostgreSQL engine with {db_url}: {e}. Falling back to SQLite.")
            return create_engine("sqlite:///./archmind.db", connect_args={"check_same_thread": False})

engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    try:
        import app.database.models  # Ensure all models are registered on Base
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
