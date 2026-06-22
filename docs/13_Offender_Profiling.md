# SENTINEL AI — Offender Profiling

## Overview

Behavioral profiling uses machine learning to classify offenders into archetypes, assess risk levels, and provide explainable insights about criminal behavior patterns.

## Feature Engineering

### Features Used

| Feature Category | Features | Source |
|-----------------|----------|--------|
| Demographics | Age, gender, education, occupation | Person |
| Criminal History | Prior convictions, recidivism count, crime type severity | Accused/Offender |
| Behavioral | Weapon use, time of day, day of week, victim type | CrimeIncident |
| Social | Gang affiliation, organization links, territory | Gang/Org |
| Modus Operandi | Entry method, target selection, escape pattern | CrimeIncident.MO |

### Feature Processing

```python
FEATURES = [
    "age", "gender_encoded", "education_level", "crime_type_severity",
    "prior_convictions", "recidivism_count", "weapon_used_flag",
    "gang_affiliation_flag", "night_time_crime_flag", "weekend_crime_flag",
    "victim_known_flag", "property_crime_flag", "violent_crime_flag",
    "organized_crime_flag", "single_offender_flag"
]
```

## ML Models

### 1. Archetype Classification (KMeans + HDBSCAN)

```python
archetypes = {
    0: "Opportunistic Offender",
    1: "Organized Criminal", 
    2: "Violent Predator",
    3: "Financial Fraudster",
    4: "Gang Associate",
    5: "Situation Offender",
}
```

### 2. Risk Scoring (XGBoost)

```python
risk_levels = {
    (0.0, 0.3): "Low",
    (0.3, 0.6): "Medium",
    (0.6, 0.8): "High",
    (0.8, 1.0): "Critical"
}
```

## SHAP Explainability

```
┌─────────────────────────────────────────────────────────────┐
│  SHAP Force Plot Example                                     │
│                                                              │
│  base_value: 0.45                                            │
│                                                              │
│  Features pushing risk UP:                                   │
│    +0.25  prior_convictions = 4                              │
│    +0.15  crime_type_severity = 8                            │
│    +0.10  gang_affiliation = True                            │
│    +0.08  weapon_used = True                                 │
│                                                              │
│  Features pushing risk DOWN:                                 │
│    -0.12  education_level = graduate                         │
│    -0.05  age = 35                                           │
│                                                              │
│  Final risk score: 0.86 (CRITICAL)                           │
└─────────────────────────────────────────────────────────────┘
```

## Output Schema

```json
{
    "person_id": "uuid",
    "archetype": "Organized Criminal",
    "risk_level": "High",
    "risk_score": 0.78,
    "recidivism_probability": 0.65,
    "escalation_risk": "Medium",
    "modus_operandi_profile": {
        "preferred_time": "night",
        "preferred_day": "weekend",
        "target_type": "residential",
        "entry_method": "forced_entry",
        "group_size": "solo"
    },
    "shap_explanation": {
        "prior_convictions": 0.25,
        "crime_type_severity": 0.15,
        "gang_affiliation": 0.10
    },
    "profile_summary": "Repeat offender with organized crime affiliation..."
}
```

## API

```http
GET /api/v1/analytics/offender-profiles?archetype=organized_criminal

POST /api/v1/analytics/profile
{
    "person_id": "uuid",
    "incident_ids": ["uuid1", "uuid2"]
}
```
