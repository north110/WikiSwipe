from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite connection string; the database file will be created in the current directory
SQLALCHEMY_DATABASE_URL = "sqlite:///./wiki.db"

# For SQLite, set check_same_thread to False for multi-threaded applications (like FastAPI)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our ORM models
Base = declarative_base()
