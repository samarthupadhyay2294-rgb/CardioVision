from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "CardioVision API"
    debug: bool = True
    api_prefix: str = "/api"

    secret_key: str = "change-me-in-production-use-openssl-rand"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7

    database_url: str = f"sqlite:///{ROOT / 'data' / 'cardiovision.db'}"
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    model_path: str = str(ROOT / "ml_models" / "trained" / "heart_disease_model.pkl")
    upload_dir: str = str(ROOT / "data" / "uploads")
    pdf_dir: str = str(ROOT / "data" / "reports")

    supabase_url: str = ""
    supabase_key: str = ""
    supabase_bucket: str = "reports"

    google_client_id: str = ""
    google_client_secret: str = ""

    ocr_engine: str = "paddle"
    poppler_path: str = ""

    @property
    def resolved_poppler_path(self) -> str | None:
        if self.poppler_path and Path(self.poppler_path).exists():
            return self.poppler_path
        tools = ROOT / "tools" / "poppler"
        if tools.exists():
            for candidate in tools.rglob("pdftoppm.exe"):
                return str(candidate.parent)
        return None

    @property
    def cors_origin_list(self) -> list[str]:
        origins = [o.strip() for o in self.cors_origins.split(",") if o.strip()]
        web_url = __import__("os").environ.get("RENDER_EXTERNAL_URL", "").strip()
        if web_url and web_url not in origins:
            origins.append(web_url)
        return origins


@lru_cache
def get_settings() -> Settings:
    return Settings()
