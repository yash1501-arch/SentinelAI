# SENTINEL AI — Crime Forecasting

## Model: Prophet (Meta)

Prophet is a decomposable time-series model that handles trends, seasonality, and holiday effects — ideal for crime pattern forecasting.

## Why Prophet?

- Handles missing data and outliers
- Automatic seasonality detection (yearly, weekly, daily)
- Country-specific holiday effects (Indian holidays configured)
- Interpretable components (trend, seasonality, holiday)
- Confidence intervals on all predictions

## Forecast Dimensions

| Forecast Type | Granularity | Horizon | Model |
|--------------|-------------|---------|-------|
| Crime Volume | Daily | 30 days | Prophet |
| Hotspot Activity | Weekly | 12 weeks | Prophet |
| Gang Activity | Weekly | 8 weeks | Prophet |
| District Trends | Monthly | 6 months | Prophet |

## Configuration

```python
PROPHET_CONFIG = {
    "seasonality_mode": "multiplicative",
    "yearly_seasonality": True,
    "weekly_seasonality": True,
    "daily_seasonality": False,
    "changepoint_prior_scale": 0.05,
    "seasonality_prior_scale": 10.0,
    "holidays_prior_scale": 10.0,
    "uncertainty_samples": 1000,
    "country_holidays": "IN"
}
```

## Pipeline

```
┌──────────────┐    ┌────────────┐    ┌──────────────┐    ┌─────────┐
│  DataStore   │───▶│  Prophet   │───▶│  Forecast    │───▶│  Cache  │
│  Aggregation │    │  Fit/Predict│   │  + Intervals │    │  + Alert│
└──────────────┘    └────────────┘    └──────────────┘    └─────────┘
       │                                                  │
       │                                                  ▼
       │                                         ┌────────────────┐
       │                                         │  Anomaly Check │
       │                                         │  (>20% spike)  │
       │                                         └───────┬────────┘
       │                                                 │
       │                                          ┌──────▼────────┐
       │                                          │  Send Alert   │
       │                                          │  (Email/In-app)│
       └──────────────────────────────────────────┴───────────────┘
```

## Response Format

```json
{
    "forecast_type": "crime_volume",
    "district": "mysore",
    "model_used": "prophet",
    "confidence_level": 0.95,
    "data_points": [
        {
            "date": "2024-02-15",
            "predicted": 23.5,
            "lower_bound": 18.2,
            "upper_bound": 29.1
        }
    ],
    "components": {
        "trend": "increasing",
        "weekly_pattern": "peak_friday_saturday",
        "seasonal_strength": 0.72
    },
    "alerts": [
        {
            "type": "spike_warning",
            "message": "Predicted 35% increase in burglary next week",
            "severity": "medium"
        }
    ]
}
```

## API

```http
POST /api/v1/analytics/forecast
{
    "forecast_type": "crime_volume",
    "district": "mysore",
    "crime_type_id": "uuid-for-burglary",
    "days_ahead": 30
}
```

## Alert Thresholds

| Severity | Threshold | Action |
|----------|-----------|--------|
| Low | 10-20% above baseline | Log |
| Medium | 20-40% above baseline | Dashboard notification |
| High | 40-60% above baseline | Email alert to supervisor |
| Critical | >60% above baseline | SMS + Email + Dashboard alert |
