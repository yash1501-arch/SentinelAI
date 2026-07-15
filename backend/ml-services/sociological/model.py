"""Multi-factor correlation analysis between socio-economic indicators and crime rates."""
import os
import json
import pandas as pd
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score
import joblib

from .data import generate_sociological_data

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODELS_DIR, exist_ok=True)

FEATURES = [
    "urbanization_rate", "literacy_rate", "poverty_rate",
    "unemployment_rate", "migration_rate", "juvenile_population_pct",
    "police_per_capita", "population_density", "avg_income",
]
TARGET = "crime_rate_per_100k"


def analyze(save: bool = True) -> dict:
    df = generate_sociological_data()

    correlations = {}
    for col in FEATURES:
        r, p = stats.pearsonr(df[col], df[TARGET])
        correlations[col] = {"pearson_r": round(r, 4), "p_value": round(p, 6)}

    X = StandardScaler().fit_transform(df[FEATURES])
    y = df[TARGET].values

    model = LinearRegression()
    model.fit(X, y)
    r2 = r2_score(y, model.predict(X))

    factor_importance = sorted(
        [
            {"factor": col, "coefficient": round(float(coef), 4)}
            for col, coef in zip(FEATURES, model.coef_)
        ],
        key=lambda x: abs(x["coefficient"]),
        reverse=True,
    )

    (
        df.groupby("year")
        .agg({TARGET: "mean", **{f: "mean" for f in FEATURES}})
        .round(2)
        .to_dict(orient="index")
    )

    high_crime = df.nlargest(5, TARGET)[["district", "year", TARGET] + FEATURES].to_dict(orient="records")
    low_crime = df.nsmallest(5, TARGET)[["district", "year", TARGET] + FEATURES].to_dict(orient="records")

    results = {
        "r2_score": round(r2, 4),
        "n_districts": df["district"].nunique(),
        "n_years": df["year"].nunique(),
        "correlations": correlations,
        "factor_importance": factor_importance,
        "worst_performers": [
            {k: round(v, 2) if isinstance(v, float) else v for k, v in r.items()}
            for r in high_crime
        ],
        "best_performers": [
            {k: round(v, 2) if isinstance(v, float) else v for k, v in r.items()}
            for r in low_crime
        ],
    }

    if save:
        joblib.dump(model, os.path.join(MODELS_DIR, "regression_model.pkl"))
        df.to_csv(os.path.join(MODELS_DIR, "sociological_data.csv"), index=False)
        with open(os.path.join(MODELS_DIR, "analysis.json"), "w") as f:
            json.dump(results, f, indent=2, default=str)
        print(f"Analysis saved to {MODELS_DIR}")

    return results


def predict(features: dict) -> dict:
    model = joblib.load(os.path.join(MODELS_DIR, "regression_model.pkl"))
    X = pd.DataFrame([features])[FEATURES]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    predicted_crime_rate = float(model.predict(X_scaled)[0])

    return {"predicted_crime_rate_per_100k": round(predicted_crime_rate, 2)}


if __name__ == "__main__":
    results = analyze()
    print(json.dumps(results, indent=2, default=str))
