from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.dependencies.auth import require_admin, require_user
from database.connection import get_db
from database.models import Prediction, Report, User

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard")
def user_dashboard(user=Depends(require_user), db: Session = Depends(get_db)):
    reports = db.query(Report).filter(Report.user_id == user.id).all()
    preds = (
        db.query(Prediction)
        .join(Report)
        .filter(Report.user_id == user.id)
        .order_by(Prediction.created_at.desc())
        .all()
    )

    risks = [p.risk_pct for p in preds if p.risk_pct is not None]
    avg_risk = sum(risks) / len(risks) if risks else 0
    trend = [
        {
            "date": p.created_at.strftime("%Y-%m-%d"),
            "risk_pct": p.risk_pct,
            "category": p.risk_category,
        }
        for p in reversed(preds[-12:])
    ]

    latest = None
    if preds:
        p = preds[0]
        latest = {
            "report_id": p.report_id,
            "risk_pct": p.risk_pct,
            "risk_category": p.risk_category,
            "disease_risks": p.disease_risks,
        }

    return {
        "health_summary": {
            "total_reports": len(reports),
            "average_risk": round(avg_risk, 1),
            "latest_risk": risks[0] if risks else None,
        },
        "latest_report": latest,
        "risk_trend": trend,
        "recent_reports": [
            {
                "report_id": r.id,
                "file_name": r.file_name,
                "status": r.status,
                "created_at": r.created_at.isoformat(),
            }
            for r in sorted(reports, key=lambda x: x.created_at, reverse=True)[:5]
        ],
    }


@router.get("/profile")
def profile(user=Depends(require_user)):
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "is_admin": user.is_admin,
        "created_at": user.created_at.isoformat(),
    }


@router.get("/admin/overview")
def admin_overview(_=Depends(require_admin), db: Session = Depends(get_db)):
    user_count = db.query(func.count(User.id)).scalar()
    report_count = db.query(func.count(Report.id)).scalar()
    pred_count = db.query(func.count(Prediction.id)).scalar()
    avg_risk = db.query(func.avg(Prediction.risk_pct)).scalar() or 0

    risk_buckets = {"low": 0, "moderate": 0, "high": 0, "critical": 0}
    for p in db.query(Prediction.risk_pct).all():
        r = p[0]
        if r < 35:
            risk_buckets["low"] += 1
        elif r < 55:
            risk_buckets["moderate"] += 1
        elif r < 75:
            risk_buckets["high"] += 1
        else:
            risk_buckets["critical"] += 1

    return {
        "users": user_count,
        "reports": report_count,
        "predictions": pred_count,
        "average_risk": round(float(avg_risk), 1),
        "risk_distribution": risk_buckets,
        "system_health": "healthy",
        "storage_status": "ok",
        "api_status": "operational",
    }


@router.get("/admin/users")
def admin_users(_=Depends(require_admin), db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.created_at.desc()).limit(100).all()
    return {
        "users": [
            {
                "id": u.id,
                "email": u.email,
                "full_name": u.full_name,
                "is_admin": u.is_admin,
                "created_at": u.created_at.isoformat(),
            }
            for u in users
        ]
    }
