from pydantic import BaseModel


class AnalysisResult(BaseModel):
    report_id: str
    status: str
    risk_pct: float | None = None
    risk_category: str | None = None
    disease_risks: dict | None = None
    shap_factors: list | None = None
    explanations: list | None = None
    recommendations: dict | None = None
    features: dict | None = None
    parameters: list | None = None
    patient_summary: dict | None = None
    pdf_url: str | None = None
