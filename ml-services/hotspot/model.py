"""DBSCAN-based crime hotspot detection with cluster analysis."""
import os
import json
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import joblib

from .data import generate_hotspot_data

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODELS_DIR, exist_ok=True)


def train(eps: float = 0.003, min_samples: int = 10, save: bool = True) -> dict:
    df = generate_hotspot_data(2000)
    coords = df[["latitude", "longitude"]].values
    scaler = StandardScaler()
    coords_scaled = scaler.fit_transform(coords)

    model = DBSCAN(eps=eps, min_samples=min_samples, metric="euclidean", n_jobs=-1)
    labels = model.fit_predict(coords_scaled)

    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise = int((labels == -1).sum())

    df["cluster"] = labels
    cluster_stats = []

    for cid in range(n_clusters):
        mask = labels == cid
        cluster_points = coords[mask]
        center_lat = float(cluster_points[:, 0].mean())
        center_lon = float(cluster_points[:, 1].mean())
        density = int(mask.sum())
        radius = float(np.max(np.linalg.norm(cluster_points - cluster_points.mean(axis=0), axis=1)))

        crime_types = df.loc[mask, "crime_type"].value_counts(normalize=True).to_dict()
        cluster_stats.append({
            "cluster_id": int(cid),
            "center_lat": round(center_lat, 6),
            "center_lon": round(center_lon, 6),
            "density": density,
            "radius_meters": round(radius * 111000, 2),
            "crime_type_distribution": {k: round(v, 3) for k, v in crime_types.items()},
        })

    silhouette = float(silhouette_score(coords_scaled[labels != -1], labels[labels != -1])) if n_clusters > 1 else 0

    results = {
        "n_clusters": n_clusters,
        "n_noise_points": n_noise,
        "silhouette_score": round(silhouette, 4),
        "clusters": sorted(cluster_stats, key=lambda x: x["density"], reverse=True),
    }

    if save:
        joblib.dump(model, os.path.join(MODELS_DIR, "dbscan_model.pkl"))
        joblib.dump(scaler, os.path.join(MODELS_DIR, "scaler.pkl"))
        df.to_csv(os.path.join(MODELS_DIR, "clustered_data.csv"), index=False)
        with open(os.path.join(MODELS_DIR, "results.json"), "w") as f:
            json.dump(results, f, indent=2)
        print(f"Model saved to {MODELS_DIR}")

    return results


def predict(latitudes: list, longitudes: list) -> list:
    model = joblib.load(os.path.join(MODELS_DIR, "dbscan_model.pkl"))
    scaler = joblib.load(os.path.join(MODELS_DIR, "scaler.pkl"))

    coords = np.column_stack([latitudes, longitudes])
    coords_scaled = scaler.transform(coords)
    labels = model.fit_predict(coords_scaled)

    return [{"latitude": lat, "longitude": lon, "cluster": int(label)}
            for lat, lon, label in zip(latitudes, longitudes, labels)]


if __name__ == "__main__":
    results = train()
    print(json.dumps(results, indent=2, default=str))
