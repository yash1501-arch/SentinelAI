# SENTINEL AI — ML Architecture

## Overview

The ML Layer provides pattern discovery, prediction, profiling, and anomaly detection capabilities across the crime intelligence platform.

## ML Models

| Model | Library | Purpose | Training Frequency |
|-------|---------|---------|-------------------|
| DBSCAN | Scikit-learn | Crime hotspot detection | Weekly |
| XGBoost | XGBoost | Offender risk scoring | Monthly |
| Prophet | Prophet | Crime time-series forecasting | Daily |
| Isolation Forest | Scikit-learn | Financial anomaly detection | Weekly |
| Sentence Transformers | SBERT | Text embeddings | Static |
| NetworkX | NetworkX | Graph analytics | On-demand |
| KMeans/HDBSCAN | Scikit-learn | Offender archetype clustering | Monthly |

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ML PIPELINE                               │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌───────────────┐    ┌───────────────┐ │
│  │ Feature Store │───▶│  ML Models    │───▶│  Prediction   │ │
│  │ (DataStore)   │    │  (Pickle/ONNX)│    │  Store        │ │
│  └──────────────┘    └───────────────┘    └───────────────┘ │
│         │                    │                    │           │
│         ▼                    ▼                    ▼           │
│  ┌───────────────────────────────────────────────────────┐   │
│  │              SHAP Explainer                           │   │
│  │  (Feature importance, explanation per prediction)     │   │
│  └───────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 1. DBSCAN — Crime Hotspot Detection

```python
from sklearn.cluster import DBSCAN
import numpy as np

def detect_hotspots(latitudes, longitudes, eps=0.01, min_samples=5):
    coords = np.column_stack([latitudes, longitudes])
    clustering = DBSCAN(eps=eps, min_samples=min_samples, metric='haversine')
    labels = clustering.fit_predict(np.radians(coords))

    hotspots = []
    for cluster_id in set(labels):
        if cluster_id == -1:  # noise
            continue
        cluster_points = coords[labels == cluster_id]
        hotspots.append({
            "cluster_id": int(cluster_id),
            "center_lat": float(np.mean(cluster_points[:, 0])),
            "center_lon": float(np.mean(cluster_points[:, 1])),
            "density": len(cluster_points),
            "radius": calculate_cluster_radius(cluster_points),
        })
    return hotspots
```

## 2. XGBoost — Offender Risk Scoring

```python
import xgboost as xgb
import shap

class OffenderRiskModel:
    FEATURES = [
        "age", "prior_convictions", "crime_type_severity",
        "weapon_used", "gang_affiliation", "recidivism_count",
        "education_level", "employment_status", "substance_abuse"
    ]

    def predict(self, features: dict) -> dict:
        df = pd.DataFrame([features])[self.FEATURES]
        risk_score = self.model.predict(df)[0]
        explainer = shap.TreeExplainer(self.model)
        shap_values = explainer.shap_values(df)
        return {
            "risk_score": float(risk_score),
            "risk_level": self._get_risk_level(risk_score),
            "shap_explanation": {
                str(self.FEATURES[i]): float(shap_values[0][i])
                for i in range(len(self.FEATURES))
            }
        }
```

## 3. Prophet — Crime Forecasting

```python
from prophet import Prophet

class CrimeForecaster:
    def forecast(self, df, periods=30):
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
            seasonality_mode='multiplicative'
        )
        model.add_country_holidays('IN')
        model.fit(df)
        future = model.make_future_dataframe(periods=periods)
        forecast = model.predict(future)
        return {
            "dates": forecast['ds'].tail(periods).tolist(),
            "predictions": forecast['yhat'].tail(periods).tolist(),
            "lower_bound": forecast['yhat_lower'].tail(periods).tolist(),
            "upper_bound": forecast['yhat_upper'].tail(periods).tolist(),
        }
```

## 4. Isolation Forest — Financial Anomaly Detection

```python
from sklearn.ensemble import IsolationForest

def detect_suspicious_transactions(transactions_df):
    model = IsolationForest(
        contamination=0.1,
        random_state=42
    )
    features = ['amount', 'transaction_hour', 'is_cross_border',
                'account_age_days', 'frequency_7d']
    predictions = model.fit_predict(transactions_df[features])
    # -1 = anomaly, 1 = normal
    transactions_df['is_anomaly'] = predictions == -1
    return transactions_df[transactions_df['is_anomaly']]
```

## Model Storage

Models are serialized (pickle/joblib) and stored in:
- Catalyst Stratus Object Storage for production
- Local `ml-services/models/` for development

## Batch Inference Pipeline

```
Schedule (Catalyst Scheduler)
    │
    ├─ Daily 06:00 → Prophet Forecast → Store → Alert if threshold
    ├─ Weekly Sun 00:00 → DBSCAN Hotspots → Update hotspots table
    ├─ Monthly 1st → XGBoost Retrain → Evaluate → Deploy
    └─ Every 15min → Embedding Sync → Qdrant upsert
```
