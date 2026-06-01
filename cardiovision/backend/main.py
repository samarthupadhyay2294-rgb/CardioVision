import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.api.routes import analysis, auth, dashboard
from backend.core.config import get_settings
from backend.services.storage import ensure_dirs
from database.connection import init_db

settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    ensure_dirs()
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.pdf_dir).mkdir(parents=True, exist_ok=True)
    Path(ROOT / "data").mkdir(parents=True, exist_ok=True)
    init_db()
    import os

    if os.environ.get("RENDER") != "true":
        try:
            from ai_engine.ocr.engine import _get_easyocr_reader

            _get_easyocr_reader()
        except Exception:
            pass
    model_path = Path(settings.model_path)
    if not model_path.exists():
        import subprocess

        train_cmd = [sys.executable, str(ROOT / "scripts" / "train_model.py")]
        subprocess.run(train_cmd, cwd=str(ROOT), check=False)
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

prefix = settings.api_prefix
app.include_router(auth.router, prefix=prefix)
app.include_router(analysis.router, prefix=prefix)
app.include_router(dashboard.router, prefix=prefix)


@app.get("/health")
def health():
    return {"status": "ok", "service": "cardiovision-api"}


@app.get("/")
def root():
    return {"message": "CardioVision API", "docs": "/docs"}
