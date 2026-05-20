import os
import uuid
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./scholr.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class SearchHistory(Base):
    __tablename__ = "search_history"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    module = Column(String, nullable=False)
    query = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class DocumentAsset(Base):
    __tablename__ = "document_assets"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
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
    document_id = Column(String, ForeignKey("document_assets.id"), nullable=False, index=True)
    page_number = Column(Integer, nullable=False, default=1)
    chunk_index = Column(Integer, nullable=False, default=0)
    document_name = Column(String, nullable=False, default="Uploaded document")
    content = Column(Text, nullable=False)
    citation_label = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    inspector = inspect(engine)
    try:
        columns = {column["name"] for column in inspector.get_columns("document_chunks")}
    except Exception:
        columns = set()

    if "document_name" not in columns and columns:
        with engine.begin() as connection:
            connection.execute(
                text("ALTER TABLE document_chunks ADD COLUMN document_name VARCHAR DEFAULT 'Uploaded document' NOT NULL")
            )
