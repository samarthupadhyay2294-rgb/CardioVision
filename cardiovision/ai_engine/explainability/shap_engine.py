import numpy as np
import shap

from ai_engine.prediction.features import FEATURE_DESCRIPTIONS, FEATURE_NAMES, NORMAL_RANGES


def _get_xgb_model(model):
    if hasattr(model, "named_estimators_"):
        return model.named_estimators_.get("xgb")
    if hasattr(model, "estimators_") and hasattr(model, "estimators"):
        for i, (name, _) in enumerate(model.estimators):
            if name == "xgb":
                return model.estimators_[i]
    return None


def explain_with_shap(model, scaler, X_train_raw, input_values: dict):
    xgb_model = _get_xgb_model(model)
    if xgb_model is None:
        return []

    explainer = shap.TreeExplainer(xgb_model)
    row = np.array([input_values[f] for f in FEATURE_NAMES]).reshape(1, -1)
    row_scaled = scaler.transform(row)
    shap_values = explainer.shap_values(row_scaled)
    sv = shap_values[0] if getattr(shap_values, "ndim", 1) == 2 else shap_values[0]

    pairs = sorted(zip(FEATURE_NAMES, sv), key=lambda x: abs(x[1]), reverse=True)
    result = []
    total = sum(abs(sv)) or 1.0
    for feat, val in pairs[:10]:
        direction = "increase" if val > 0 else "decrease"
        pct = float(round(abs(float(val)) / float(total) * 100, 1))
        result.append(
            {
                "feature": feat,
                "label": FEATURE_DESCRIPTIONS.get(feat, feat),
                "contribution_pct": pct,
                "direction": direction,
                "raw_shap": float(val),
            }
        )
    return result


def explain_predictions(input_values: dict, shap_factors: list) -> list:
    explanations = []
    v = input_values

    if shap_factors:
        for item in shap_factors[:5]:
            feat = item["feature"]
            pct = item["contribution_pct"]
            direction = "↑" if item["direction"] == "increase" else "↓"
            actual = v[feat]
            desc = FEATURE_DESCRIPTIONS.get(feat, feat)
            norm = NORMAL_RANGES.get(feat)
            flag = ""
            if norm:
                lo, hi = norm
                if feat == "hdl":
                    flag = " ⚠ Low HDL" if actual < lo else ""
                elif actual > hi:
                    flag = f" ⚠ High (normal <{hi})"
                elif actual < lo:
                    flag = f" ⚠ Low (normal >{lo})"
            explanations.append(
                f"{direction} {desc}: {actual}{flag}  [+{pct}% risk contribution]"
            )
    else:
        checks = [
            (v["chol"] > 240, f"High Cholesterol = {v['chol']} mg/dl"),
            (v["ldl"] > 160, f"High LDL = {v['ldl']} mg/dl"),
            (v["trestbps"] > 140, f"High Blood Pressure = {v['trestbps']} mmHg"),
            (v["age"] > 55, f"Age = {v['age']}"),
            (v["smoking"] == 1, "Active Smoker"),
            (v["diabetes_history"] == 1, "Diabetes History"),
            (v["family_history"] == 1, "Family History of Heart Disease"),
            (v["bmi"] > 30, f"Obese BMI = {v['bmi']}"),
            (v["hba1c"] > 6.5, f"Elevated HbA1c = {v['hba1c']}%"),
            (v["triglycerides"] > 200, f"High Triglycerides = {v['triglycerides']} mg/dl"),
        ]
        for condition, msg in checks:
            if condition:
                explanations.append(msg)

    return explanations if explanations else ["No significant risk factors detected."]
