from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config import AppConfig
from src.database.models import Base

# SQLite for MVP. Switch to PostgreSQL string for Prod.
DATABASE_URL = f"sqlite:///{AppConfig.SQL_DB_PATH}"

# check_same_thread=False is needed for SQLite with Streamlit/FastAPI multi-threading
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize database tables."""
    # Create parent directory if not exists
    import os
    os.makedirs(os.path.dirname(AppConfig.SQL_DB_PATH), exist_ok=True)
    
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency for database session (for FastAPI or Context Managers)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
