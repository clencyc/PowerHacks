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
        from sqlalchemy import text
        
        # Test connection first
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        
        # Create tables
        SQLModel.metadata.create_all(engine)
        print("✅ Database tables created successfully")
        return True
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        return False

def get_session():
    """Get database session"""
    with Session(engine) as session:
        yield session
