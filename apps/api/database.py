import os
from sqlmodel import SQLModel, create_engine, Session

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./safespace.db")

# Handle PostgreSQL URL format for SQLAlchemy
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(
    DATABASE_URL,
    echo=os.getenv("ENVIRONMENT") == "development"
)

def create_db_and_tables():
    """Create all database tables"""
    try:
        SQLModel.metadata.create_all(engine)
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        raise e

def get_session():
    """Get database session"""
    with Session(engine) as session:
        yield session
