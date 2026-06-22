"""
Offender Profiling — XGBoost + SHAP risk scoring module.

Trains a multi-output model predicting:
- Risk score (regression, 0-1)
- Recidivism probability (regression, 0-1)
- Escalation risk (classification: Low/Medium/High/Critical)
- Archetype classification (6 classes)

Saves models to ml-services/profiling/models/
"""
