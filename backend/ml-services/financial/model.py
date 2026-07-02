"""Financial fraud detection using Isolation Forest + XGBoost."""
import os
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from xgboost import XGBClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, roc_auc_score, precision_recall_curve
import joblib

from .data import generate_transactions

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODELS_DIR, exist_ok=True)

FEATURES = ["amount", "amount_log", "hour", "day_of_week", "is_night"]


def train(save: bool = True) -> dict:
    df = generate_transactions(5000, 100)

    type_encoder = LabelEncoder()
    df["transaction_type_enc"] = type_encoder.fit_transform(df["transaction_type"])

    all_features = FEATURES + ["transaction_type_enc"]

    X = df[all_features]
    y = df["is_fraud"]

    iso_forest = IsolationForest(
        n_estimators=200, contamination=0.02, random_state=42, n_jobs=-1
    )
    df["anomaly_score"] = iso_forest.fit_predict(X)
    df["anomaly_score"] = (df["anomaly_score"] == -1).astype(int)

    xgb_model = XGBClassifier(
        n_estimators=150, max_depth=6, learning_rate=0.1,
        scale_pos_weight=50, eval_metric="aucpr", random_state=42,
    )
    xgb_model.fit(X, y)

    y_prob = xgb_model.predict_proba(X)[:, 1]
    y_pred = xgb_model.predict(X)

    auc_roc = roc_auc_score(y, y_prob)
    precision, recall, _ = precision_recall_curve(y, y_prob)
    avg_precision = float(np.mean(precision[recall >= 0.5])) if any(recall >= 0.5) else 0.0

    report = classification_report(y, y_pred, output_dict=True, zero_division=0)

    feature_importance = sorted(
        [
            {"feature": col, "importance": round(float(imp), 4)}
            for col, imp in zip(all_features, xgb_model.feature_importances_)
        ],
        key=lambda x: x["importance"],
        reverse=True,
    )

    results = {
        "auc_roc": round(auc_roc, 4),
        "avg_precision_at_50_recall": round(avg_precision, 4),
        "fraud_detection_rate": round(report["1"]["recall"], 4),
        "precision": round(report["1"]["precision"], 4),
        "f1_score": round(report["1"]["f1-score"], 4),
        "feature_importance": feature_importance,
        "n_transactions": len(df),
        "n_fraud": int(y.sum()),
        "fraud_pct": round(float(y.mean() * 100), 2),
    }

    if save:
        joblib.dump(iso_forest, os.path.join(MODELS_DIR, "isolation_forest.pkl"))
        joblib.dump(xgb_model, os.path.join(MODELS_DIR, "xgb_fraud_model.pkl"))
        joblib.dump(type_encoder, os.path.join(MODELS_DIR, "type_encoder.pkl"))
        joblib.dump(all_features, os.path.join(MODELS_DIR, "features.pkl"))
        with open(os.path.join(MODELS_DIR, "metrics.json"), "w") as f:
            json.dump(results, f, indent=2, default=str)
        print(f"Models saved to {MODELS_DIR}")

    return results


def predict(transaction: dict) -> dict:
    xgb_model = joblib.load(os.path.join(MODELS_DIR, "xgb_fraud_model.pkl"))
    type_encoder = joblib.load(os.path.join(MODELS_DIR, "type_encoder.pkl"))
    all_features = joblib.load(os.path.join(MODELS_DIR, "features.pkl"))

    txn = transaction.copy()
    txn["amount_log"] = np.log1p(txn.get("amount", 0))
    txn["transaction_type_enc"] = int(type_encoder.transform([txn.get("transaction_type", "transfer")])[0])

    X = pd.DataFrame([txn])[all_features]
    prob = float(xgb_model.predict_proba(X)[0, 1])
    pred = int(xgb_model.predict(X)[0])

    return {
        "is_fraudulent": bool(pred),
        "fraud_probability": round(prob, 4),
        "risk_level": "high" if prob > 0.7 else "medium" if prob > 0.3 else "low",
    }


if __name__ == "__main__":
    metrics = train()
    print(json.dumps(metrics, indent=2))
