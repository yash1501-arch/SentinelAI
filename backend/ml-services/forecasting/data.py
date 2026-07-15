"""Synthetic crime time-series data generator."""
import pandas as pd
import numpy as np


def generate_daily_crime_data(
    start_date: str = "2022-01-01",
    end_date: str = "2025-12-31",
    base_crime_rate: float = 50,
    seed: int = 42,
) -> pd.DataFrame:
    np.random.seed(seed)
    dates = pd.date_range(start=start_date, end=end_date, freq="D")
    n = len(dates)

    trend = np.linspace(0, base_crime_rate * 0.3, n)
    seasonal_weekly = 5 * np.sin(2 * np.pi * dates.dayofweek / 7)
    seasonal_yearly = 10 * np.sin(2 * np.pi * dates.dayofyear / 365)
    noise = np.random.normal(0, 5, n)

    crime_count = np.clip(base_crime_rate + trend + seasonal_weekly + seasonal_yearly + noise, 0, None)

    return pd.DataFrame({
        "ds": dates,
        "y": crime_count.round().astype(int),
        "day_of_week": dates.dayofweek,
        "month": dates.month,
        "year": dates.year,
    })
