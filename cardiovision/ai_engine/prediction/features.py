FEATURE_NAMES = [
    "age",
    "sex",
    "cp",
    "trestbps",
    "chol",
    "fbs",
    "restecg",
    "thalach",
    "exang",
    "oldpeak",
    "slope",
    "ca",
    "thal",
    "bmi",
    "hdl",
    "ldl",
    "triglycerides",
    "smoking",
    "family_history",
    "diabetes_history",
    "hba1c",
]

FEATURE_DESCRIPTIONS = {
    "age": "Age (years)",
    "sex": "Sex (1=Male, 0=Female)",
    "cp": "Chest Pain Type (0-3)",
    "trestbps": "Resting Blood Pressure (mmHg)",
    "chol": "Serum Cholesterol (mg/dl)",
    "fbs": "Fasting Blood Sugar > 120mg/dl (1=Yes)",
    "restecg": "Resting ECG Results (0-2)",
    "thalach": "Max Heart Rate Achieved",
    "exang": "Exercise Induced Angina (1=Yes)",
    "oldpeak": "ST Depression (exercise vs rest)",
    "slope": "Slope of Peak Exercise ST Segment",
    "ca": "Number of Major Vessels (0-3)",
    "thal": "Thalassemia (0-3)",
    "bmi": "Body Mass Index",
    "hdl": "HDL Cholesterol (mg/dl)",
    "ldl": "LDL Cholesterol (mg/dl)",
    "triglycerides": "Triglycerides (mg/dl)",
    "smoking": "Smoking Status (1=Yes)",
    "family_history": "Family History of Heart Disease (1=Yes)",
    "diabetes_history": "Diabetes History (1=Yes)",
    "hba1c": "HbA1c (%)",
}

NORMAL_RANGES = {
    "trestbps": (90, 120),
    "chol": (0, 200),
    "bmi": (18.5, 24.9),
    "hdl": (60, 100),
    "ldl": (0, 100),
    "triglycerides": (0, 150),
    "hba1c": (4.0, 5.6),
    "thalach": (100, 200),
    "oldpeak": (0, 1.0),
    "ca": (0, 0),
}

DEFAULT_FEATURE_VALUES = {
    "age": 50,
    "sex": 1,
    "cp": 0,
    "trestbps": 120,
    "chol": 200,
    "fbs": 0,
    "restecg": 0,
    "thalach": 150,
    "exang": 0,
    "oldpeak": 0.0,
    "slope": 1,
    "ca": 0,
    "thal": 2,
    "bmi": 25.0,
    "hdl": 50,
    "ldl": 100,
    "triglycerides": 150,
    "smoking": 0,
    "family_history": 0,
    "diabetes_history": 0,
    "hba1c": 5.5,
}


def risk_category(risk_pct: float) -> str:
    if risk_pct >= 75:
        return "Critical Risk"
    if risk_pct >= 55:
        return "High Risk"
    if risk_pct >= 35:
        return "Moderate Risk"
    return "Low Risk"
