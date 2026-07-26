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

if os.environ.get("RENDER") == "true":
    # Log only the scheme/host, never credentials, to confirm what's wired up.
    from sqlalchemy.engine import make_url

    try:
        _safe = make_url(db_url)
        print(
            f"[connection] Using database driver={_safe.drivername} "
            f"host={_safe.host} dbname={_safe.database}"
        )
    except Exception as exc:  # pragma: no cover - diagnostic only
        print(f"[connection] Could not pre-validate DATABASE_URL: {exc}")

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
