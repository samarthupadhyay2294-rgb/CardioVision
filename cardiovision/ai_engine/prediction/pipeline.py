from pathlib import Path

from ai_engine.explainability.shap_engine import explain_predictions, explain_with_shap
from ai_engine.extraction.parameter_extractor import (
    build_parameter_table,
    build_patient_summary,
    map_to_ml_features,
)
from ai_engine.prediction.features import FEATURE_DESCRIPTIONS, risk_category
from ai_engine.prediction.model import (
    disease_specific_risks,
    load_model_bundle,
    predict_risk_percentage,
)
from ai_engine.recommendations.engine import generate_recommendations
from reports.pdf_generator import generate_pdf_report

_MODEL_CACHE = None


def get_model_bundle(model_path: Path):
    global _MODEL_CACHE
    if _MODEL_CACHE is None:
        _MODEL_CACHE = load_model_bundle(model_path)
    return _MODEL_CACHE


def run_analysis(
    features: dict,
    extracted_meta: dict,
    model_path: Path,
    pdf_output: Path | None = None,
) -> dict:
    model, scaler, X_train_raw = get_model_bundle(model_path)
    risk_pct = predict_risk_percentage(model, scaler, features)
    category = risk_category(risk_pct)
    disease_risks = disease_specific_risks(features, risk_pct)
    shap_factors = explain_with_shap(model, scaler, X_train_raw, features)
    explanations = explain_predictions(features, shap_factors)
    recommendations = generate_recommendations(features, risk_pct)

    result = {
        "risk_pct": risk_pct,
        "risk_category": category,
        "disease_risks": disease_risks,
        "shap_factors": shap_factors,
        "explanations": explanations,
        "recommendations": recommendations,
        "features": features,
        "feature_descriptions": FEATURE_DESCRIPTIONS,
        "parameters": build_parameter_table(features),
        "patient_summary": build_patient_summary(extracted_meta, features),
        "extracted_meta": extracted_meta,
    }

    if pdf_output:
        generate_pdf_report(
            features,
            risk_pct,
            category,
            disease_risks,
            explanations,
            recommendations,
            shap_factors,
            str(pdf_output),
        )
        result["pdf_path"] = str(pdf_output)

    return result


def run_from_extracted(extracted: dict, model_path: Path, pdf_output: Path | None = None):
    features = map_to_ml_features(extracted)
    return run_analysis(features, extracted, model_path, pdf_output)
