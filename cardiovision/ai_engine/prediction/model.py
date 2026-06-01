import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import VotingClassifier
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier

from ai_engine.prediction.features import FEATURE_NAMES

try:
    from catboost import CatBoostClassifier

    CATBOOST_AVAILABLE = True
except ImportError:
    CATBOOST_AVAILABLE = False


def build_ensemble():
    xgb = XGBClassifier(
        n_estimators=300,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        eval_metric="logloss",
        random_state=42,
    )
    lgbm = LGBMClassifier(
        n_estimators=300,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        verbose=-1,
    )
    estimators = [("xgb", xgb), ("lgbm", lgbm)]
    if CATBOOST_AVAILABLE:
        cat = CatBoostClassifier(
            iterations=300,
            depth=5,
            learning_rate=0.05,
            random_seed=42,
            verbose=0,
        )
        estimators.append(("cat", cat))
    return VotingClassifier(estimators=estimators, voting="soft")


def preprocess(df: pd.DataFrame):
    df = df.dropna()
    X = df[FEATURE_NAMES].copy()
    y = df["target"].copy()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    return X_train_scaled, X_test_scaled, y_train, y_test, scaler, X_train, X_test


def train_model(X_train, y_train, X_test, y_test):
    model = build_ensemble()
    model.fit(X_train, y_train)
    test_proba = model.predict_proba(X_test)[:, 1]
    metrics = {
        "train_accuracy": float(
            accuracy_score(y_train, model.predict(X_train))
        ),
        "test_accuracy": float(accuracy_score(y_test, model.predict(X_test))),
        "test_roc_auc": float(roc_auc_score(y_test, test_proba)),
        "report": classification_report(y_test, model.predict(X_test)),
    }
    return model, metrics


def predict_risk_percentage(model, scaler, input_values: dict) -> float:
    row = np.array([input_values[f] for f in FEATURE_NAMES]).reshape(1, -1)
    row_scaled = scaler.transform(row)
    prob = model.predict_proba(row_scaled)[0][1]
    return round(float(prob * 100), 1)


def disease_specific_risks(input_values: dict, base_risk: float) -> dict:
    v = input_values
    br = base_risk / 100.0

    def sigmoid(x):
        return 1 / (1 + np.exp(-x))

    cad_score = (
        0.04 * (v["age"] - 45)
        + 0.005 * (v["ldl"] - 100)
        + 0.004 * (v["chol"] - 200)
        + 0.6 * v["smoking"]
        + 0.4 * v["family_history"]
        + 0.015 * (v["trestbps"] - 120)
        + 2.0 * br
    )
    htn_score = (
        0.04 * (v["age"] - 40)
        + 0.04 * (v["bmi"] - 25)
        + 0.02 * (v["trestbps"] - 120)
        + 0.4 * v["diabetes_history"]
        + 0.005 * (v["triglycerides"] - 150)
        + 1.5 * br
    )
    hf_score = (
        0.03 * (v["age"] - 50)
        + 0.3 * v["exang"]
        + 0.2 * v["diabetes_history"]
        + 0.04 * (v["bmi"] - 25)
        + 0.1 * v["oldpeak"]
        + 1.0 * br
    )
    arr_score = (
        0.02 * (v["age"] - 40)
        + 0.3 * (v["restecg"] > 0)
        + 0.2 * (v["thal"] > 1)
        + 0.3 * v["exang"]
        + 0.5 * br
    )
    ath_score = (
        0.03 * (v["age"] - 45)
        + 0.006 * (v["ldl"] - 100)
        + 0.005 * (v["chol"] - 200)
        + 0.5 * v["smoking"]
        + 0.004 * (v["triglycerides"] - 150)
        + 0.3 * v["diabetes_history"]
        + 1.8 * br
    )

    return {
        "Coronary Artery Disease": float(round(sigmoid(cad_score) * 100, 1)),
        "Hypertension": float(round(sigmoid(htn_score) * 100, 1)),
        "Heart Failure": float(round(sigmoid(hf_score) * 100, 1)),
        "Arrhythmia": float(round(sigmoid(arr_score) * 100, 1)),
        "Atherosclerosis": float(round(sigmoid(ath_score) * 100, 1)),
    }


def save_model_bundle(model, scaler, X_train_raw: pd.DataFrame, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(
            {"model": model, "scaler": scaler, "X_train_raw": X_train_raw},
            f,
        )


def load_model_bundle(path: Path):
    with open(path, "rb") as f:
        data = pickle.load(f)
    return data["model"], data["scaler"], data["X_train_raw"]
