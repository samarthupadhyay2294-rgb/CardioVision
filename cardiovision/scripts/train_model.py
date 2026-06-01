"""Train ensemble model and save to ml_models/trained/."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd

from ai_engine.prediction.model import preprocess, save_model_bundle, train_model

DATASET = ROOT / "ml_models" / "datasets" / "heart_disease_data_enhanced.csv"
OUTPUT = ROOT / "ml_models" / "trained" / "heart_disease_model.pkl"


def main():
    if not DATASET.exists():
        alt = ROOT.parent / "heart_disease_data_enhanced.csv"
        if alt.exists():
            DATASET.parent.mkdir(parents=True, exist_ok=True)
            import shutil

            shutil.copy(alt, DATASET)
        else:
            raise FileNotFoundError("Dataset not found: " + str(DATASET))

    df = pd.read_csv(DATASET)
    X_train_s, X_test_s, y_train, y_test, scaler, X_train_raw, _ = preprocess(df)
    model, metrics = train_model(X_train_s, y_train, X_test_s, y_test)
    save_model_bundle(model, scaler, X_train_raw, OUTPUT)
    print("Model saved to", OUTPUT)
    print(metrics)


if __name__ == "__main__":
    main()
