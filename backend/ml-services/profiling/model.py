"""Offender profiling model — XGBoost + SHAP explanation pipeline."""
import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error, accuracy_score, r2_score
from xgboost import XGBClassifier, XGBRegressor
import shap

from .data import generate_dataset, split_data, OFFENDER_ARCHETYPES, RISK_LEVELS

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODELS_DIR, exist_ok=True)

FEATURES = [
    "age", "prior_cases", "is_repeat_offender", "education_score",
    "employment_score", "is_male", "substance_abuse", "gang_affiliation",
    "mental_health_issues", "weapon_use", "violence_score",
]


def train(save: bool = True) -> dict:
    df = generate_dataset(5000)
    train_df, test_df = split_data(df)

    X_train = train_df[FEATURES]
    y_risk = train_df["risk_score"]
    y_recidivism = train_df["recidivism_probability"]
    y_escalation = train_df["escalation_risk"]
    y_archetype = train_df["archetype"]

    X_test = test_df[FEATURES]
    y_risk_test = test_df["risk_score"]
    y_recidivism_test = test_df["recidivism_probability"]
    y_escalation_test = test_df["escalation_risk"]
    y_archetype_test = test_df["archetype"]

    escalation_encoder = LabelEncoder()
    y_escalation_enc = escalation_encoder.fit_transform(y_escalation)

    archetype_encoder = LabelEncoder()
    y_archetype_enc = archetype_encoder.fit_transform(y_archetype)

    risk_model = XGBRegressor(
        n_estimators=200, max_depth=6, learning_rate=0.08,
        subsample=0.8, colsample_bytree=0.8, random_state=42,
    )
    risk_model.fit(X_train, y_risk)

    recidivism_model = XGBRegressor(
        n_estimators=200, max_depth=6, learning_rate=0.08,
        subsample=0.8, colsample_bytree=0.8, random_state=42,
    )
    recidivism_model.fit(X_train, y_recidivism)

    escalation_model = XGBClassifier(
        n_estimators=200, max_depth=4, learning_rate=0.1,
        objective="multi:softprob", num_class=4, random_state=42,
    )
    escalation_model.fit(X_train, y_escalation_enc)

    archetype_model = XGBClassifier(
        n_estimators=200, max_depth=4, learning_rate=0.1,
        objective="multi:softprob", num_class=6, random_state=42,
    )
    archetype_model.fit(X_train, y_archetype_enc)

    risk_pred = risk_model.predict(X_test)
    recidivism_pred = recidivism_model.predict(X_test)
    escalation_pred = escalation_model.predict(X_test)
    archetype_pred = archetype_model.predict(X_test)

    risk_mse = mean_squared_error(y_risk_test, risk_pred)
    risk_r2 = r2_score(y_risk_test, risk_pred)
    recidivism_mse = mean_squared_error(y_recidivism_test, recidivism_pred)
    recidivism_r2 = r2_score(y_recidivism_test, recidivism_pred)
    escalation_acc = accuracy_score(
        escalation_encoder.transform(y_escalation_test), escalation_pred
    )
    archetype_acc = accuracy_score(
        archetype_encoder.transform(y_archetype_test), archetype_pred
    )

    explainer = shap.TreeExplainer(risk_model)
    shap_values = explainer.shap_values(X_test[:100])

    results = {
        "risk_mse": round(risk_mse, 4),
        "risk_r2": round(risk_r2, 4),
        "recidivism_mse": round(recidivism_mse, 4),
        "recidivism_r2": round(recidivism_r2, 4),
        "escalation_accuracy": round(escalation_acc, 4),
        "archetype_accuracy": round(archetype_acc, 4),
        "shap_top_feature": FEATURES[int(np.argmax(np.abs(shap_values).mean(axis=0)))],
    }

    if save:
        joblib.dump(risk_model, os.path.join(MODELS_DIR, "risk_model.pkl"))
        joblib.dump(recidivism_model, os.path.join(MODELS_DIR, "recidivism_model.pkl"))
        joblib.dump(escalation_model, os.path.join(MODELS_DIR, "escalation_model.pkl"))
        joblib.dump(archetype_model, os.path.join(MODELS_DIR, "archetype_model.pkl"))
        joblib.dump(escalation_encoder, os.path.join(MODELS_DIR, "escalation_encoder.pkl"))
        joblib.dump(archetype_encoder, os.path.join(MODELS_DIR, "archetype_encoder.pkl"))
        joblib.dump(FEATURES, os.path.join(MODELS_DIR, "features.pkl"))
        with open(os.path.join(MODELS_DIR, "metrics.json"), "w") as f:
            json.dump(results, f, indent=2)
        print(f"Models saved to {MODELS_DIR}")

    return results


def predict(features: dict) -> dict:
    risk_model = joblib.load(os.path.join(MODELS_DIR, "risk_model.pkl"))
    recidivism_model = joblib.load(os.path.join(MODELS_DIR, "recidivism_model.pkl"))
    escalation_model = joblib.load(os.path.join(MODELS_DIR, "escalation_model.pkl"))
    archetype_model = joblib.load(os.path.join(MODELS_DIR, "archetype_model.pkl"))
    escalation_encoder = joblib.load(os.path.join(MODELS_DIR, "escalation_encoder.pkl"))
    archetype_encoder = joblib.load(os.path.join(MODELS_DIR, "archetype_encoder.pkl"))
    saved_features = joblib.load(os.path.join(MODELS_DIR, "features.pkl"))

    X = pd.DataFrame([features])[saved_features]

    risk = float(risk_model.predict(X)[0])
    recidivism = float(recidivism_model.predict(X)[0])
    escalation_idx = int(escalation_model.predict(X)[0])
    archetype_idx = int(archetype_model.predict(X)[0])

    escalation_label = escalation_encoder.inverse_transform([escalation_idx])[0]
    archetype_label = archetype_encoder.inverse_transform([archetype_idx])[0]

    explainer = shap.TreeExplainer(risk_model)
    shap_values = explainer.shap_values(X)
    shap_explanation = dict(zip(saved_features, np.round(shap_values[0], 4)))

    return {
        "risk_score": round(risk, 4),
        "recidivism_probability": round(recidivism, 4),
        "escalation_risk": escalation_label,
        "archetype": archetype_label,
        "shap_explanation": shap_explanation,
    }


if __name__ == "__main__":
    metrics = train()
    print(json.dumps(metrics, indent=2))
