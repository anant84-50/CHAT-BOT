import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from ..config import settings

logger = logging.getLogger("chatbot")

is_sqlite = False
engine = None

db_url = settings.DATABASE_URL

if db_url.startswith("postgresql"):
    try:
        # Quick 2-second timeout to test if Postgres is running
        test_engine = create_engine(db_url, connect_args={"connect_timeout": 2})
        with test_engine.connect():
            pass
        engine = test_engine
        is_sqlite = False
        logger.info("Connected to PostgreSQL successfully.")
    except Exception as e:
        logger.warning(f"Could not connect to PostgreSQL ({e}). Using local SQLite database.")
        db_url = "sqlite:///./chatbot.db"
        engine = create_engine(db_url, connect_args={"check_same_thread": False})
        is_sqlite = True
else:
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    is_sqlite = True

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

