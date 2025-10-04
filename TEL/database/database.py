from sqlmodel import SQLModel, Session, create_engine

# =============================================================================
# DATABASE SETUP
# =============================================================================

# Database setup
DATABASE_URL = "sqlite:///database.db"
engine = create_engine(DATABASE_URL, echo=False)  # Set to True for SQL debugging

def get_session() -> Session:
    return Session(engine)

def create_db_and_tables():
    """Create database tables and populate with initial data."""
    SQLModel.metadata.create_all(engine)
