import os
import uuid
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

configured_database_url = os.getenv("DATABASE_URL", "").strip()
sqlite_path = os.getenv("SQLITE_PATH", "/data/scholr.db").strip()
# Render's persistent disk should be mounted at /data so SQLite survives deploys.
DATABASE_URL = configured_database_url if configured_database_url.startswith("postgresql") else f"sqlite:///{sqlite_path}"

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


DEFAULT_TENANT_USER_ID = "public-demo"
DEFAULT_TENANT_SESSION_ID = "public-session"


class SearchHistory(Base):
    __tablename__ = "search_history"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, default=DEFAULT_TENANT_USER_ID, index=True)
    session_id = Column(String, nullable=False, default=DEFAULT_TENANT_SESSION_ID, index=True)
    module = Column(String, nullable=False)
    query = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class DocumentAsset(Base):
    __tablename__ = "document_assets"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, default=DEFAULT_TENANT_USER_ID, index=True)
    session_id = Column(String, nullable=False, default=DEFAULT_TENANT_SESSION_ID, index=True)
    title = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    storage_path = Column(Text, nullable=False)
    mime_type = Column(String, nullable=False, default="application/pdf")
    status = Column(String, nullable=False, default="processing")
    page_count = Column(Integer, nullable=False, default=0)
    chunk_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, default=DEFAULT_TENANT_USER_ID, index=True)
    document_id = Column(String, ForeignKey("document_assets.id"), nullable=False, index=True)
    page_number = Column(Integer, nullable=False, default=1)
    chunk_index = Column(Integer, nullable=False, default=0)
    document_name = Column(String, nullable=False, default="Uploaded document")
    content = Column(Text, nullable=False)
    citation_label = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class UsageLedger(Base):
    __tablename__ = "usage_ledger"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    session_id = Column(String, nullable=False, default=DEFAULT_TENANT_SESSION_ID, index=True)
    scope = Column(String, nullable=False, index=True)
    amount = Column(Integer, nullable=False, default=1)
    period = Column(String, nullable=False, default="daily", index=True)
    period_key = Column(String, nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    module = Column(String, nullable=False)
    query = Column(Text, nullable=False)
    rating = Column(String, nullable=False)
    response_length = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class Waitlist(Base):
    __tablename__ = "waitlist"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False)
    source = Column(String, default="landing_page")
    created_at = Column(DateTime, default=datetime.utcnow)


class UserSession(Base):
    __tablename__ = "user_sessions"

    session_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    auth_provider = Column(String, nullable=False, default="public")
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_seen_at = Column(DateTime, nullable=False, default=datetime.utcnow)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    inspector = inspect(engine)

    def table_columns(table_name: str) -> set[str]:
        try:
            return {column["name"] for column in inspector.get_columns(table_name)}
        except Exception:
            return set()

    migrations: dict[str, list[tuple[str, str]]] = {
        "document_chunks": [
            ("document_name", "ALTER TABLE document_chunks ADD COLUMN document_name VARCHAR DEFAULT 'Uploaded document' NOT NULL"),
            ("user_id", f"ALTER TABLE document_chunks ADD COLUMN user_id VARCHAR DEFAULT '{DEFAULT_TENANT_USER_ID}' NOT NULL"),
        ],
        "search_history": [
            ("user_id", f"ALTER TABLE search_history ADD COLUMN user_id VARCHAR DEFAULT '{DEFAULT_TENANT_USER_ID}' NOT NULL"),
            ("session_id", f"ALTER TABLE search_history ADD COLUMN session_id VARCHAR DEFAULT '{DEFAULT_TENANT_SESSION_ID}' NOT NULL"),
        ],
        "document_assets": [
            ("user_id", f"ALTER TABLE document_assets ADD COLUMN user_id VARCHAR DEFAULT '{DEFAULT_TENANT_USER_ID}' NOT NULL"),
            ("session_id", f"ALTER TABLE document_assets ADD COLUMN session_id VARCHAR DEFAULT '{DEFAULT_TENANT_SESSION_ID}' NOT NULL"),
        ],
    }

    with engine.begin() as connection:
        for table_name, statements in migrations.items():
            columns = table_columns(table_name)
            if not columns:
                continue
            for column_name, statement in statements:
                if column_name not in columns:
                    connection.execute(text(statement))
