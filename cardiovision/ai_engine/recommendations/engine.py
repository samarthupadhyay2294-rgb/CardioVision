def generate_recommendations(input_values: dict, risk_pct: float) -> dict:
    v = input_values
    diet, exercise, lifestyle, follow_up, monitoring = [], [], [], [], []

    if v["chol"] > 200 or v["ldl"] > 130:
        diet.append("Reduce saturated fats; choose olive oil, nuts, and avocados.")
        diet.append("Eat fatty fish (salmon, mackerel) 2× per week for Omega-3.")
    if v["triglycerides"] > 150:
        diet.append("Limit refined carbs and sugars; avoid sweetened beverages.")
    if v["bmi"] > 25:
        diet.append("Target a calorie deficit of 300–500 kcal/day for gradual weight loss.")
    if v["hdl"] < 40:
        diet.append("Increase HDL by consuming whole grains, beans, and moderate nuts.")
    if v["hba1c"] > 5.7 or v["diabetes_history"]:
        diet.append("Adopt a low glycaemic-index diet; limit white rice and bread.")
    if v["trestbps"] > 130:
        diet.append("Follow a DASH diet; reduce sodium intake to <2,300 mg/day.")
    diet.append("Eat ≥5 servings of vegetables and fruits daily.")
    diet.append("Stay well hydrated — aim for 8–10 glasses of water per day.")

    if risk_pct > 70:
        exercise.append("Start with supervised cardiac rehabilitation exercises.")
        exercise.append("Begin with 15–20 min of light walking; increase gradually.")
    elif risk_pct > 40:
        exercise.append("30 min of moderate aerobic activity (brisk walk, cycling) 5×/week.")
        exercise.append("Add resistance training 2×/week to improve insulin sensitivity.")
    else:
        exercise.append("150 min/week of moderate aerobic activity (WHO recommendation).")
        exercise.append("Include yoga or stretching for stress and BP reduction.")
    if v["bmi"] > 30:
        exercise.append("Low-impact activities (swimming, elliptical) to protect joints.")
    if v["smoking"]:
        exercise.append("Join a smoking cessation program — smoking multiplies cardiac risk.")

    if v["smoking"]:
        lifestyle.append("Quit smoking; seek cessation support within 30 days.")
    if v["bmi"] > 27:
        lifestyle.append("Aim for 5–10% body weight reduction over 6 months.")
    if v["trestbps"] > 130:
        lifestyle.append("Limit alcohol; monitor home blood pressure twice weekly.")
    lifestyle.append("Manage stress with mindfulness, sleep hygiene (7–8 hours/night).")
    lifestyle.append("Reduce sedentary time; stand and move every hour.")

    if risk_pct > 70:
        follow_up.append("Consult a cardiologist within the next 7 days.")
        follow_up.append("Request: Stress ECG, Echocardiogram, Full Lipid Panel, HbA1c.")
    elif risk_pct > 40:
        follow_up.append("Schedule a cardiology review within 4 weeks.")
        follow_up.append("Request: Fasting lipid profile, glucose tolerance test, 24-hr BP monitor.")
    else:
        follow_up.append("Annual preventive health check-up recommended.")
        follow_up.append("Maintain current lifestyle and reassess in 12 months.")
    if v["diabetes_history"] or v["hba1c"] > 6.5:
        follow_up.append("Endocrinologist consultation for diabetes management.")
    if v["family_history"]:
        follow_up.append("Inform cardiologist of family history for genetic risk screening.")

    monitoring.append("Track resting heart rate and blood pressure weekly.")
    monitoring.append("Repeat lipid panel every 3–6 months if elevated.")
    if v["diabetes_history"] or v["hba1c"] > 5.7:
        monitoring.append("Monitor fasting glucose and HbA1c every 3 months.")
    monitoring.append("Log symptoms: chest pain, shortness of breath, palpitations.")

    return {
        "diet": diet,
        "exercise": exercise,
        "lifestyle": lifestyle,
        "follow_up": follow_up,
        "monitoring": monitoring,
        "doctor": follow_up,
    }
