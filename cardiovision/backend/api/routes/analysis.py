from pathlib import Path

from fastapi import APIRouter, Depends, File, Header, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.core.config import get_settings
from backend.dependencies.auth import get_optional_user, require_user
from backend.schemas.analysis import AnalysisResult
from backend.services.analysis import process_file_pipeline
from backend.services.storage import save_upload, upload_to_supabase
from backend.utils.json_safe import to_json_safe
from database.connection import get_db
from database.models import (
    ExtractedParameters,
    GuestSession,
    Prediction,
    Recommendation,
    Report,
)

router = APIRouter(tags=["analysis"])
settings = get_settings()


def _get_or_create_guest(db: Session, token: str | None) -> GuestSession:
    if token:
        existing = (
            db.query(GuestSession).filter(GuestSession.session_token == token).first()
        )
        if existing:
            return existing
    import secrets

    session = GuestSession(session_token=secrets.token_urlsafe(32))
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.post("/upload")
async def upload_report(
    file: UploadFile = File(...),
    x_guest_session: str | None = Header(None),
    user_guest=Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    user, guest = user_guest
    if not guest and not x_guest_session:
        guest = _get_or_create_guest(db, None)
    elif x_guest_session and not guest:
        guest = _get_or_create_guest(db, x_guest_session)

    content = await file.read()
    if len(content) > 20 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 20MB)")

    allowed = {".pdf", ".jpg", ".jpeg", ".png"}
    ext = Path(file.filename or "upload.bin").suffix.lower()
    if ext not in allowed:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    local_path, safe_name = save_upload(content, file.filename or "report")
    await upload_to_supabase(content, safe_name)

    report = Report(
        user_id=user.id if user else None,
        guest_session_id=guest.id if guest else None,
        file_name=file.filename or safe_name,
        file_path=local_path,
        file_type=ext.lstrip("."),
        status="uploaded",
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    return {
        "report_id": report.id,
        "guest_session": guest.session_token if guest else None,
        "file_name": report.file_name,
        "status": report.status,
    }


@router.post("/analyze/{report_id}", response_model=AnalysisResult)
def analyze_report(
    report_id: str,
    user_guest=Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    report.status = "processing"
    db.commit()

    try:
        result = process_file_pipeline(report.file_path, report_id)
    except Exception as exc:
        report.status = "failed"
        db.commit()
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    report.status = "completed"
    report.ocr_text = result.get("ocr_text")

    safe = to_json_safe(result)

    prediction = Prediction(
        report_id=report.id,
        risk_pct=float(safe["risk_pct"]),
        risk_category=str(safe["risk_category"]),
        disease_risks=safe["disease_risks"],
        shap_factors=safe["shap_factors"],
        explanations=safe["explanations"],
        features=safe["features"],
        pdf_path=result.get("pdf_path"),
    )
    db.add(prediction)
    db.flush()

    extracted_row = ExtractedParameters(
        report_id=report.id,
        raw_data=safe.get("extracted_raw", {}),
        ml_features=safe["features"],
        parameter_table=safe["parameters"],
        patient_summary=safe["patient_summary"],
    )
    db.add(extracted_row)

    rec = Recommendation(prediction_id=prediction.id, content=safe["recommendations"])
    db.add(rec)
    db.commit()
    db.refresh(prediction)

    pdf_url = f"/api/pdf/{report_id}" if result.get("pdf_path") else None

    return AnalysisResult(
        report_id=report_id,
        status="completed",
        risk_pct=safe["risk_pct"],
        risk_category=safe["risk_category"],
        disease_risks=safe["disease_risks"],
        shap_factors=safe["shap_factors"],
        explanations=safe["explanations"],
        recommendations=safe["recommendations"],
        features=safe["features"],
        parameters=safe["parameters"],
        patient_summary=safe["patient_summary"],
        pdf_url=pdf_url,
    )


@router.post("/pipeline")
async def full_pipeline(
    file: UploadFile = File(...),
    x_guest_session: str | None = Header(None),
    user_guest=Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    upload_resp = await upload_report(file, x_guest_session, user_guest, db)
    return analyze_report(upload_resp["report_id"], user_guest, db)


@router.get("/pdf/{report_id}")
def download_pdf(report_id: str, db: Session = Depends(get_db)):
    prediction = (
        db.query(Prediction)
        .join(Report)
        .filter(Report.id == report_id)
        .first()
    )
    if not prediction or not prediction.pdf_path or not Path(prediction.pdf_path).exists():
        raise HTTPException(status_code=404, detail="PDF not found")
    return FileResponse(
        prediction.pdf_path,
        media_type="application/pdf",
        filename=f"cardiovision_{report_id}.pdf",
    )


@router.get("/history")
def history(user=Depends(require_user), db: Session = Depends(get_db)):
    reports = (
        db.query(Report)
        .filter(Report.user_id == user.id)
        .order_by(Report.created_at.desc())
        .limit(50)
        .all()
    )
    items = []
    for r in reports:
        pred = r.prediction
        items.append(
            {
                "report_id": r.id,
                "file_name": r.file_name,
                "status": r.status,
                "created_at": r.created_at.isoformat(),
                "risk_pct": pred.risk_pct if pred else None,
                "risk_category": pred.risk_category if pred else None,
            }
        )
    return {"reports": items}


@router.get("/report/{report_id}")
def get_report(report_id: str, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report or not report.prediction:
        raise HTTPException(status_code=404, detail="Report not found")
    p = report.prediction
    e = report.extracted
    rec = p.recommendations
    return AnalysisResult(
        report_id=report_id,
        status=report.status,
        risk_pct=p.risk_pct,
        risk_category=p.risk_category,
        disease_risks=p.disease_risks,
        shap_factors=p.shap_factors,
        explanations=p.explanations,
        recommendations=rec.content if rec else {},
        features=p.features,
        parameters=e.parameter_table if e else [],
        patient_summary=e.patient_summary if e else {},
        pdf_url=f"/api/pdf/{report_id}",
    )


@router.delete("/report/{report_id}")
def delete_report(report_id: str, user=Depends(require_user), db: Session = Depends(get_db)):
    report = (
        db.query(Report)
        .filter(Report.id == report_id, Report.user_id == user.id)
        .first()
    )
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    db.delete(report)
    db.commit()
    return {"deleted": True}
