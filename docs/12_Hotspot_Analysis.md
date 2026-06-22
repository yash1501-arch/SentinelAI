# SENTINEL AI — Hotspot Analysis

## Methodology: DBSCAN Clustering

DBSCAN (Density-Based Spatial Clustering of Applications with Noise) identifies high-density crime areas without requiring pre-specified cluster counts.

## Input Features

| Feature | Source | Format |
|---------|--------|--------|
| Latitude | Location records | float |
| Longitude | Location records | float |
| Crime Type | CrimeIncident | string |
| Timestamp | CrimeIncident | datetime |
| Severity | CrimeType | int |

## Algorithm Configuration

```python
DBSCAN_CONFIG = {
    "eps": 0.01,          # ~1km radius (in radians for haversine)
    "min_samples": 5,     # Minimum points to form cluster
    "metric": "haversine", # Geographic distance
    "algorithm": "ball_tree"
}
```

## Implementation Flow

```
┌────────────┐   ┌──────────────┐   ┌──────────────┐   ┌────────────┐
│ PostgreSQL │──▶│  Geo Query   │──▶│   DBSCAN     │──▶│  Store     │
│ Locations  │   │  (30 days)   │   │  Clustering  │   │  Hotspots  │
└────────────┘   └──────────────┘   └──────────────┘   └─────┬──────┘
                                                              │
                                                              ▼
                                                      ┌──────────────┐
                                                      │  Mapbox      │
                                                      │  Heatmap     │
                                                      │  + Cluster   │
                                                      │  Overlay     │
                                                      └──────────────┘
```

## Output Schema

```json
{
    "cluster_id": 1,
    "center_latitude": 12.345,
    "center_longitude": 76.789,
    "crime_count": 23,
    "radius_meters": 850,
    "crime_type_distribution": {
        "burglary": 10,
        "theft": 8,
        "assault": 5
    },
    "risk_score": 0.78,
    "peak_time": "20:00-23:00",
    "peak_day": "Saturday"
}
```

## Mapbox Visualization

- **Heatmap Layer:** Crime density as gradient heat
- **Cluster Layer:** DBSCAN clusters as concentric circles
- **Individual Points:** Each crime incident as clickable marker
- **Filter Controls:** Crime type, date range, severity

## API

```http
GET /api/v1/analytics/hotspots?district=mysore&days=30

Response:
{
    "hotspots": [...],
    "total_clusters": 12,
    "noise_points": 45,
    "analysis_date": "2024-01-15T00:00:00Z",
    "config": { "eps": 0.01, "min_samples": 5 }
}
```
