from pathlib import Path

from ai_engine.extraction.parameter_extractor import (
    build_parameter_table,
    build_patient_summary,
    map_to_ml_features,
)
from ai_engine.ocr.engine import extract_text_from_file, parse_ocr_text
from ai_engine.prediction.pipeline import run_analysis, run_from_extracted
from backend.core.config import get_settings

settings = get_settings()


def process_file_pipeline(file_path: str, report_id: str) -> dict:
    model_path = Path(settings.model_path)
    if not model_path.exists():
        raise FileNotFoundError(
            "ML model not found. Run: python scripts/train_model.py"
        )

    text = extract_text_from_file(file_path, engine=settings.ocr_engine)
    extracted = parse_ocr_text(text)
    extracted["ocr_engine"] = settings.ocr_engine

    pdf_path = Path(settings.pdf_dir) / f"{report_id}.pdf"
    result = run_from_extracted(extracted, model_path, pdf_output=pdf_path)

    features = map_to_ml_features(extracted)
    result["ocr_text"] = text[:5000]
    result["extracted_raw"] = {k: v for k, v in extracted.items() if k != "raw_text"}
    result["parameters"] = build_parameter_table(features)
    result["patient_summary"] = build_patient_summary(extracted, features)
    result["report_id"] = report_id
    return result
