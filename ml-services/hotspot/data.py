"""Synthetic crime location data generator."""
import numpy as np
import pandas as pd


def generate_hotspot_data(
    n_points: int = 2000,
    n_clusters: int = 5,
    center_lat: float = 12.9716,
    center_lon: float = 77.5946,
    seed: int = 42,
) -> pd.DataFrame:
    np.random.seed(seed)
    points = []

    cluster_centers = [
        (center_lat + np.random.uniform(-0.05, 0.05), center_lon + np.random.uniform(-0.05, 0.05))
        for _ in range(n_clusters)
    ]

    for i in range(n_points):
        cluster = np.random.choice(n_clusters)
        lat, lon = cluster_centers[cluster]
        lat += np.random.normal(0, 0.008)
        lon += np.random.normal(0, 0.008)
        crime_type = np.random.choice(
            ["theft", "assault", "robbery", "burglary", "homicide", "fraud"],
            p=[0.3, 0.2, 0.15, 0.15, 0.05, 0.15],
        )
        timestamp = pd.Timestamp("2024-01-01") + pd.Timedelta(
            days=np.random.randint(0, 365), hours=np.random.randint(0, 24)
        )
        points.append(
            {"latitude": lat, "longitude": lon, "crime_type": crime_type, "timestamp": timestamp}
        )

    df = pd.DataFrame(points)
    noise_mask = np.random.random(n_points) < 0.1
    df.loc[noise_mask, "latitude"] += np.random.uniform(-0.1, 0.1, noise_mask.sum())
    df.loc[noise_mask, "longitude"] += np.random.uniform(-0.1, 0.1, noise_mask.sum())

    return df
