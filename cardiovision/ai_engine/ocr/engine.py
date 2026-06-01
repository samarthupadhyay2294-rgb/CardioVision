import re
import tempfile
from pathlib import Path


def _preprocess_image(path: str):
    try:
        import cv2
        import numpy as np

        img = cv2.imread(path)
        if img is None:
            return path
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        denoised = cv2.fastNlMeansDenoising(enhanced, None, 10, 7, 21)
        tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        cv2.imwrite(tmp.name, denoised)
        return tmp.name
    except Exception:
        return path


def _pdf_to_image(path: str) -> str:
    from pdf2image import convert_from_path

    imgs = convert_from_path(path, dpi=200, first_page=1, last_page=3)
    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    imgs[0].save(tmp.name)
    return tmp.name


def run_paddleocr(path: str) -> str:
    from paddleocr import PaddleOCR

    ocr = PaddleOCR(use_angle_cls=True, lang="en", show_log=False)
    work_path = path
    if path.lower().endswith(".pdf"):
        work_path = _pdf_to_image(path)
    else:
        work_path = _preprocess_image(path)
    result = ocr.ocr(work_path, cls=True)
    lines = []
    if result and result[0]:
        for line in result[0]:
            if line and len(line) > 1:
                lines.append(line[1][0])
    return " ".join(lines)


_EASYOCR_READER = None


def _get_easyocr_reader():
    global _EASYOCR_READER
    if _EASYOCR_READER is None:
        import easyocr

        _EASYOCR_READER = easyocr.Reader(["en"], gpu=False)
    return _EASYOCR_READER


def run_easyocr(path: str) -> str:
    reader = _get_easyocr_reader()
    work_path = path
    if path.lower().endswith(".pdf"):
        work_path = _pdf_to_image(path)
    else:
        work_path = _preprocess_image(path)
    results = reader.readtext(work_path)
    return " ".join([r[1] for r in results])


def extract_text_from_pdf_directly(pdf_path: str) -> str:
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text.strip()
    except Exception:
        return ""


def extract_text_from_file(file_path: str, engine: str = "paddle") -> str:
    path = str(file_path)
    if path.lower().endswith(".pdf"):
        direct_text = extract_text_from_pdf_directly(path)
        if direct_text:
            return direct_text

    if engine == "paddle":
        try:
            return run_paddleocr(path)
        except Exception:
            pass
    try:
        return run_easyocr(path)
    except Exception:
        return ""


PATTERNS = {
    "age": r"\bage[\s:=]+(\d{1,3})",
    "trestbps": r"(?:systolic|bp|blood pressure)[\s:=]+(\d{2,3})",
    "chol": r"(?:total cholesterol|cholesterol(?:\s+total)?)[\s:=]+(\d{2,3})",
    "ldl": r"(?:ldl(?:\s+cholesterol)?|ldl-c)[\s:=]+(\d{2,3})",
    "hdl": r"(?:hdl(?:\s+cholesterol)?|hdl-c)[\s:=]+(\d{2,3})",
    "triglycerides": r"(?:triglycerides|trig)[\s:=]+(\d{2,3})",
    "bmi": r"bmi[\s:=]+(\d{1,2}\.?\d?)",
    "hba1c": r"(?:hba1c|a1c)[\s:=]+(\d{1,2}\.?\d?)",
    "fbs": r"(?:fbs|fasting (?:blood )?sugar|glucose)[\s:=]+(\d{2,3})",
    "thalach": r"(?:heart rate|hr|pulse)[\s:=]+(\d{2,3})",
    "spo2": r"(?:spo2|sp o2|oxygen)[\s:=]+(\d{2,3})",
    "diastolic": r"diastolic[\s:=]+(\d{2,3})",
    "pr_interval": r"pr[\s-]*interval[\s:=]+(\d{2,3})",
    "qrs_duration": r"qrs[\s:=]+(\d{2,3})",
    "qt_interval": r"qt[\s-]*(?:interval)?[\s:=]+(\d{2,3})",
    "ejection_fraction": r"ejection fraction[\s:=]+(\d{1,3})",
    "height": r"height[\s:=]+(\d{2,3})",
    "weight": r"weight[\s:=]+(\d{2,3})",
}


def parse_ocr_text(text: str) -> dict:
    extracted = {"raw_text": text[:8000]}
    text_lower = text.lower()
    for field, pattern in PATTERNS.items():
        m = re.search(pattern, text_lower)
        if m:
            val = m.group(1)
            extracted[field] = float(val) if "." in val else int(val)

    if "fbs" in extracted and extracted["fbs"] > 120:
        extracted["fbs_flag"] = 1

    extracted["smoking"] = int(
        bool(re.search(r"\bsmoker\b|\bsmoking\b|tobacco", text_lower))
    )
    extracted["diabetes_history"] = int(
        bool(re.search(r"\bdiabetes\b|\bdiabetic\b", text_lower))
    )
    extracted["family_history"] = int(bool(re.search(r"family history", text_lower)))

    name_match = re.search(r"(?:patient|name)[\s:]+([A-Za-z\s]{2,40})", text, re.I)
    if name_match:
        extracted["patient_name"] = name_match.group(1).strip()

    gender_m = re.search(r"\b(male|female)\b", text_lower)
    if gender_m:
        extracted["gender"] = gender_m.group(1)
        extracted["sex"] = 1 if gender_m.group(1) == "male" else 0

    return extracted
