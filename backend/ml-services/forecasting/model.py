"""Crime forecasting using Meta Prophet."""
import os
import json
import pickle
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error

from .data import generate_daily_crime_data

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODELS_DIR, exist_ok=True)


def train(periods: int = 90, save: bool = True) -> dict:
    df = generate_daily_crime_data()
    df_train = df.iloc[:-periods].copy()
    df_test = df.iloc[-periods:].copy()

    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        seasonality_mode="multiplicative",
        changepoint_prior_scale=0.05,
        seasonality_prior_scale=10,
        interval_width=0.95,
    )

    model.add_seasonality(name="monthly", period=30.5, fourier_order=5)
    model.add_regressor("day_of_week")
    model.add_regressor("month")

    model.fit(df_train)

    forecast = model.predict(df_test.drop(columns=["y"]))

    y_true = df_test["y"].values
    y_pred = forecast["yhat"].values
    forecast["yhat_lower"].values
    forecast["yhat_upper"].values

    mae = mean_absolute_error(y_true, y_pred)
    mape = mean_absolute_percentage_error(y_true, y_pred)

    future = model.make_future_dataframe(periods=90)
    future["day_of_week"] = future["ds"].dt.dayofweek
    future["month"] = future["ds"].dt.month
    future_forecast = model.predict(future)

    results = {
        "mae": round(mae, 2),
        "mape": round(mape, 4),
        "forecast_days": 90,
        "training_days": len(df_train),
        "estimated_daily_average": round(float(future_forecast["yhat"].tail(90).mean()), 1),
    }

    if save:
        with open(os.path.join(MODELS_DIR, "prophet_model.pkl"), "wb") as f:
            pickle.dump(model, f)
        forecast_df = future_forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(90)
        forecast_df.to_csv(os.path.join(MODELS_DIR, "forecast.csv"), index=False)
        with open(os.path.join(MODELS_DIR, "metrics.json"), "w") as f:
            json.dump(results, f, indent=2)
        print(f"Model saved to {MODELS_DIR}")

    return results


def predict(days: int = 30) -> list:
    with open(os.path.join(MODELS_DIR, "prophet_model.pkl"), "rb") as f:
        model = pickle.load(f)

    future = model.make_future_dataframe(periods=days)
    future["day_of_week"] = future["ds"].dt.dayofweek
    future["month"] = future["ds"].dt.month
    forecast = model.predict(future)

    recent = forecast.tail(days)
    return [
        {
            "date": str(row["ds"].date()),
            "predicted_value": round(row["yhat"], 1),
            "lower_bound": round(row["yhat_lower"], 1),
            "upper_bound": round(row["yhat_upper"], 1),
        }
        for _, row in recent.iterrows()
    ]


if __name__ == "__main__":
    metrics = train()
    print(json.dumps(metrics, indent=2))
