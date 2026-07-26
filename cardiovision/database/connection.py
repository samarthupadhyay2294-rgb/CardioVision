import logging
import os
from pathlib import Path
from urllib.parse import urlparse

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from backend.core.config import get_settings

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[1]
SQLITE_FALLBACK = f"sqlite:///{ROOT / 'data' / 'cardiovision.db'}"


def _normalize_database_url(url: str) -> str:
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


def _mask_database_url(url: str) -> str:
    parsed = urlparse(url)
    host = parsed.hostname or "unknown"
    return f"{parsed.scheme}://***@{host}{parsed.path or ''}"


def _candidate_database_urls() -> list[str]:
    settings = get_settings()
    urls: list[str] = []

    primary = _normalize_database_url(settings.database_url)
    if primary and not primary.startswith("sqlite"):
        urls.append(primary)

    external = os.environ.get("DATABASE_EXTERNAL_URL", "").strip()
    if external:
        external = _normalize_database_url(external)
        if external not in urls:
            urls.append(external)

    return urls


def _get_working_engine():
    is_render = os.environ.get("RENDER") == "true"
    last_error: Exception | None = None

    for db_url in _candidate_database_urls():
        try:
            eng = create_engine(db_url, pool_pre_ping=True)
            with eng.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Database connection established: %s", _mask_database_url(db_url))
            return eng
        except Exception as exc:
            last_error = exc
            logger.warning(
                "Failed to connect to database (%s): %s",
                _mask_database_url(db_url),
                exc,
            )

    if is_render:
        host = urlparse(_candidate_database_urls()[0]).hostname if _candidate_database_urls() else "unknown"
        raise RuntimeError(
            "Could not connect to PostgreSQL on Render. "
            f"The hostname '{host}' could not be resolved. "
            "This usually means DATABASE_URL points to a deleted or expired database. "
            "In the Render dashboard: create or open your PostgreSQL instance, copy the "
            "Internal Database URL, set it as DATABASE_URL on cardiovision-api, and redeploy."
        ) from last_error

    logger.warning(
        "Failed to connect to primary database (%s). Falling back to SQLite: %s",
        last_error,
        SQLITE_FALLBACK,
    )
    Path(ROOT / "data").mkdir(parents=True, exist_ok=True)
    return create_engine(
        SQLITE_FALLBACK,
        connect_args={"check_same_thread": False},
        pool_pre_ping=True,
    )


engine = _get_working_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from database import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
