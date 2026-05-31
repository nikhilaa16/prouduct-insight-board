import os
import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql import text

# Database connection settings
DB_USER = "postgres"
DB_PASSWORD = "qwerty"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "feedloop_db"

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
DEFAULT_DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/postgres"

# Declarative Base for models
Base = declarative_base()

class FeedbackItem(Base):
    __tablename__ = "feedback_items"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(50), default="App Store")
    raw_text = Column(Text, nullable=False)
    customer_email = Column(String(100), nullable=True)
    category = Column(String(50), default="Others") # Login, Payment, UI/UX, Performance, Others
    feedback_type = Column(String(50), default="Bug") # Bug, Feature Request, Praise
    urgency_score = Column(Integer, default=1) # 1 to 5
    ai_summary = Column(String(255), nullable=True)
    status = Column(String(50), default="New") # New, Reviewed, In-Progress, Resolved
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

# Session management placeholders
engine = None
SessionLocal = None

def init_db():
    global engine, SessionLocal
    # Step 1: Connect to default postgres DB and ensure feedloop_db exists
    try:
        temp_engine = create_engine(DEFAULT_DB_URL, isolation_level="AUTOCOMMIT")
        with temp_engine.connect() as conn:
            # Check if feedloop_db exists
            result = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname='{DB_NAME}'"))
            exists = result.scalar()
            if not exists:
                conn.execute(text(f"CREATE DATABASE {DB_NAME}"))
                print(f"Database '{DB_NAME}' created successfully.")
        temp_engine.dispose()
    except Exception as e:
        print(f"Error checking/creating database '{DB_NAME}': {e}")
        # Proceed anyway, hoping database was pre-created

    # Step 2: Establish the actual connection to feedloop_db
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Step 3: Auto-create tables
    Base.metadata.create_all(bind=engine)
    print("Database tables initialized.")

def get_db():
    if SessionLocal is None:
        init_db()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
