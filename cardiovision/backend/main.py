import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse


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

origins = settings.cors_origin_list
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if "*" not in origins else ["*"],
    allow_origin_regex=r"https://.*\.onrender\.com|http://localhost:\d+|http://127\.0\.0\.1:\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(_request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc) or "Internal server error"},
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

