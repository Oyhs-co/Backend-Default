from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")

# Create engine
engine = create_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Get database session.
    
    Yields:
        Session: Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class DBSessionManager:
    """Singleton class for managing database sessions"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DBSessionManager, cls).__new__(cls)
            cls._instance.engine = create_engine(DATABASE_URL)
            cls._instance.SessionLocal = sessionmaker(
                autocommit=False, autoflush=False, bind=cls._instance.engine
            )
        return cls._instance

    def get_session(self) -> Session:
        """
        Get a new database session.
        
        Returns:
            Session: Database session
        """
        return self.SessionLocal()

    def get_db(self) -> Generator[Session, None, None]:
        """
        Get database session as a generator.
        
        Yields:
            Session: Database session
        """
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()