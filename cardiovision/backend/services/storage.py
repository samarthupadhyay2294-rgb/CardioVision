import uuid
from pathlib import Path

from backend.core.config import get_settings

settings = get_settings()


def ensure_dirs():
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.pdf_dir).mkdir(parents=True, exist_ok=True)


def save_upload(file_bytes: bytes, filename: str) -> tuple[str, str]:
    ensure_dirs()
    ext = Path(filename).suffix.lower() or ".bin"
    safe_name = f"{uuid.uuid4().hex}{ext}"
    path = Path(settings.upload_dir) / safe_name
    path.write_bytes(file_bytes)
    return str(path), safe_name


async def upload_to_supabase(file_bytes: bytes, filename: str) -> str | None:
    if not settings.supabase_url or not settings.supabase_key:
        return None
    try:
        from supabase import create_client

        client = create_client(settings.supabase_url, settings.supabase_key)
        remote = f"uploads/{uuid.uuid4().hex}_{filename}"
        client.storage.from_(settings.supabase_bucket).upload(
            remote, file_bytes, {"content-type": "application/octet-stream"}
        )
        return client.storage.from_(settings.supabase_bucket).get_public_url(remote)
    except Exception:
        return None
