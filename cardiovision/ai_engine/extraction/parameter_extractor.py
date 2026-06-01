from ai_engine.prediction.features import DEFAULT_FEATURE_VALUES, FEATURE_NAMES, NORMAL_RANGES


def _coerce_feature(name: str, value):
    if value is None:
        return None
    if name in ("sex", "cp", "fbs", "restecg", "exang", "slope", "ca", "thal", "smoking", "family_history", "diabetes_history"):
        return int(round(float(value)))
    if name in ("age",):
        return int(round(float(value)))
    return float(value)


def map_to_ml_features(extracted: dict) -> dict:
    merged = DEFAULT_FEATURE_VALUES.copy()

    direct_map = {
        "age": "age",
        "sex": "sex",
        "trestbps": "trestbps",
        "chol": "chol",
        "ldl": "ldl",
        "hdl": "hdl",
        "triglycerides": "triglycerides",
        "bmi": "bmi",
        "hba1c": "hba1c",
        "thalach": "thalach",
        "smoking": "smoking",
        "family_history": "family_history",
        "diabetes_history": "diabetes_history",
    }

    for src, dst in direct_map.items():
        if src in extracted and extracted[src] is not None:
            coerced = _coerce_feature(dst, extracted[src])
            if coerced is not None:
                merged[dst] = coerced

    if extracted.get("fbs_flag") == 1 or (
        "fbs" in extracted and float(extracted["fbs"]) > 120
    ):
        merged["fbs"] = 1
    elif "fbs" in extracted:
        merged["fbs"] = 1 if float(extracted["fbs"]) > 120 else 0

    if "height" in extracted and "weight" in extracted:
        h = float(extracted["height"])
        w = float(extracted["weight"])
        if h > 3:
            h_m = h / 100
        else:
            h_m = h
        if h_m > 0:
            merged["bmi"] = round(w / (h_m * h_m), 1)

    for feat in FEATURE_NAMES:
        if feat not in merged or merged[feat] is None:
            merged[feat] = DEFAULT_FEATURE_VALUES[feat]

    return merged


def build_parameter_table(features: dict) -> list:
    rows = []
    for name in FEATURE_NAMES:
        value = features[name]
        norm = NORMAL_RANGES.get(name)
        status = "normal"
        if norm:
            lo, hi = norm
            if name == "hdl":
                status = "low" if value < lo else ("normal" if value >= lo else "normal")
            elif value > hi:
                status = "high"
            elif value < lo:
                status = "low"
        rows.append(
            {
                "name": name,
                "value": value,
                "label": name.replace("_", " ").title(),
                "status": status,
                "normal_range": f"{norm[0]}–{norm[1]}" if norm else None,
            }
        )
    return rows


def build_patient_summary(extracted: dict, features: dict) -> dict:
    return {
        "name": extracted.get("patient_name", "Guest Patient"),
        "age": features.get("age"),
        "gender": extracted.get("gender", "Male" if features.get("sex") == 1 else "Female"),
        "bmi": features.get("bmi"),
        "systolic_bp": features.get("trestbps"),
        "heart_rate": features.get("thalach"),
        "spo2": extracted.get("spo2"),
    }
