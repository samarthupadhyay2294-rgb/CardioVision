import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from backend.core.config import get_settings


def _normalize_database_url(url: str) -> str:
    # Strip whitespace and any accidental surrounding quotes that can sneak in
    # when copy-pasting a value into a dashboard's env var field.
    url = (url or "").strip().strip('"').strip("'").strip()

    if not url:
        raise RuntimeError(
            "DATABASE_URL is empty. On Render, open the web service's "
            "Environment tab and confirm DATABASE_URL is actually set — "
            "render.yaml's envVars only get applied automatically if the "
            "service was created via 'New > Blueprint', not if it was "
            "created by connecting the repo directly. If created manually, "
            "add DATABASE_URL yourself using the Internal/External "
            "Connection String from your Render Postgres instance."
        )

    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)

    return url


settings = get_settings()
db_url = _normalize_database_url(settings.database_url)
connect_args = {"check_same_thread": False} if db_url.startswith("sqlite") else {}

from sqlalchemy.engine import make_url

# Validate and normalize the DB URL before passing to SQLAlchemy so that
# deployments (e.g., Render) get clearer errors and common prefixes are
# handled (Render often provides `postgres://` which SQLAlchemy prefers
# `postgresql://` or an explicit driver name).
try:
    _safe = make_url(db_url)
    if os.environ.get("RENDER") == "true":
        # Log only the scheme/host, never credentials, to confirm what's wired up.
        print(
            f"[connection] Using database driver={_safe.drivername} "
            f"host={_safe.host} dbname={_safe.database}"
        )
except Exception:
    # Attempt a couple of common fixes and re-parse.
    tried = []
    alt_db = db_url
    if db_url.startswith("postgres://"):
        alt_db = db_url.replace("postgres://", "postgresql+psycopg2://", 1)
        tried.append(alt_db)
    if db_url.startswith("postgresql://"):
        alt_db2 = db_url.replace("postgresql://", "postgresql+psycopg2://", 1)
        tried.append(alt_db2)
    parsed = False
    for candidate in tried:
        try:
            _safe = make_url(candidate)
            db_url = candidate
            parsed = True
            if os.environ.get("RENDER") == "true":
                print(
                    f"[connection] Using database driver={_safe.drivername} "
                    f"host={_safe.host} dbname={_safe.database} (after automatic fix)"
                )
            break
        except Exception:
            continue
    if not parsed:
        # Sanitize the URL for logging (remove credentials) and raise a clearer error.
        try:
            from urllib.parse import urlsplit

            parts = urlsplit(db_url)
            safe_display = f"{parts.scheme}://{parts.hostname or ''}{parts.path or ''}"
        except Exception:
            safe_display = "(unable to sanitize)"
        raise RuntimeError(
            "DATABASE_URL could not be parsed by SQLAlchemy. "
            f"Sanitized value: {safe_display}."
            " Ensure the environment variable is set and formatted like: "
            "postgresql://user:pass@host:port/dbname or sqlite:///./local.db"
        )

engine = create_engine(db_url, connect_args=connect_args, pool_pre_ping=True)
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
