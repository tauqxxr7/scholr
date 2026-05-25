import os
import uuid
from datetime import datetime
import logging
import tempfile

from dotenv import load_dotenv
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, create_engine, inspect, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool

load_dotenv()

logger = logging.getLogger(__name__)
DEFAULT_SQLITE_PATH = os.path.join(tempfile.gettempdir(), "scholr.db")


def _sqlite_url_from_path(path: str) -> str:
    normalized = os.path.abspath(path).replace("\\", "/")
    return f"sqlite:///{normalized}"


def _build_database_url() -> str:
    configured_url = os.getenv("DATABASE_URL", "").strip()
    if configured_url:
        return configured_url

    sqlite_path = os.getenv("SQLITE_PATH", DEFAULT_SQLITE_PATH).strip() or DEFAULT_SQLITE_PATH
    return _sqlite_url_from_path(sqlite_path)


def _ensure_sqlite_parent_dir(url: str) -> str:
    parsed = make_url(url)
    database_path = parsed.database
    if not database_path or database_path == ":memory:":
        return url

    parent = os.path.dirname(os.path.abspath(database_path))
    if parent:
        try:
            os.makedirs(parent, exist_ok=True)
            probe_path = os.path.join(parent, ".scholr-write-probe")
            with open(probe_path, "w", encoding="utf-8") as probe:
                probe.write("ok")
            os.remove(probe_path)
        except OSError:
            fallback_url = _sqlite_url_from_path(DEFAULT_SQLITE_PATH)
            logger.warning(
                "database_startup sqlite_parent_unwritable path=%s fallback=%s",
                parent,
                os.path.abspath(DEFAULT_SQLITE_PATH),
            )
            return fallback_url
    return url


def _log_database_startup(url: str) -> None:
    parsed = make_url(url)
    if parsed.drivername.startswith("sqlite"):
        database_path = parsed.database or ":memory:"
        safe_path = database_path if database_path == ":memory:" else os.path.abspath(database_path)
        logger.info("database_startup dialect=sqlite path=%s", safe_path)
        return

    logger.info("database_startup dialect=%s path=<credentials-hidden>", parsed.drivername)


def _create_engine():
    url = _build_database_url()
    if not url.strip():
        url = f"sqlite:///{DEFAULT_SQLITE_PATH}"
    if url.startswith("sqlite:///data/"):
        # Render persistent disks are mounted at /data; tolerate the common three-slash form.
        url = url.replace("sqlite:///data/", "sqlite:////data/", 1)
    if url.startswith("sqlite"):
        url = _ensure_sqlite_parent_dir(url)
        _log_database_startup(url)
        return create_engine(
            url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    # PostgreSQL - production connection pooling.
    if url.startswith("postgres://"):
        # Render provides postgres:// but SQLAlchemy needs postgresql://.
        url = url.replace("postgres://", "postgresql://", 1)
    _log_database_startup(url)
    return create_engine(
        url,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        pool_recycle=300,
    )


engine = _create_engine()
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
    embedding_json = Column(Text, nullable=True)
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
    mode = Column(String, nullable=True)
    latency_ms = Column(Integer, nullable=True)
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
            ("embedding_json", "ALTER TABLE search_history ADD COLUMN embedding_json TEXT"),
        ],
        "document_assets": [
            ("user_id", f"ALTER TABLE document_assets ADD COLUMN user_id VARCHAR DEFAULT '{DEFAULT_TENANT_USER_ID}' NOT NULL"),
            ("session_id", f"ALTER TABLE document_assets ADD COLUMN session_id VARCHAR DEFAULT '{DEFAULT_TENANT_SESSION_ID}' NOT NULL"),
        ],
        "feedback": [
            ("mode", "ALTER TABLE feedback ADD COLUMN mode VARCHAR"),
            ("latency_ms", "ALTER TABLE feedback ADD COLUMN latency_ms INTEGER"),
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
