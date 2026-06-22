"""Synthetic socio-economic indicator data with crime correlations."""
import numpy as np
import pandas as pd

DISTRICTS = [
    "Bengaluru Urban", "Bengaluru Rural", "Mysuru", "Hubli-Dharwad",
    "Mangaluru", "Belagavi", "Kalaburagi", "Davangere",
    "Ballari", "Tumakuru", "Shivamogga", "Udupi",
]

YEARS = list(range(2018, 2025))


def generate_sociological_data(seed: int = 42) -> pd.DataFrame:
    np.random.seed(seed)
    rows = []

    for district in DISTRICTS:
        base_pop = np.random.randint(500000, 5000000)
        base_crime = np.random.randint(500, 5000)

        for i, year in enumerate(YEARS):
            pop = int(base_pop * (1 + 0.01 * i + np.random.uniform(-0.02, 0.02)))
            density = pop / np.random.uniform(100, 500)
            urbanization = min(1, max(0.2, 0.3 + 0.05 * i + np.random.uniform(-0.05, 0.05)))
            literacy = min(1, max(0.5, 0.7 + 0.01 * i + np.random.uniform(-0.03, 0.03)))
            income = np.random.normal(50000 + 3000 * i, 5000)
            poverty = max(0.01, min(0.5, 0.2 - 0.01 * i + np.random.uniform(-0.03, 0.03)))
            unemployment = max(0.01, 0.06 + np.random.uniform(-0.02, 0.02))
            migration = np.random.uniform(0.01, 0.08)
            juvenile_pct = np.random.uniform(0.15, 0.3)
            police_per_capita = np.random.uniform(1.5, 4.0)

            crime_influence = (
                0.3 * urbanization
                + 0.15 * (1 - literacy)
                + 0.2 * poverty
                + 0.15 * unemployment
                + 0.1 * migration
                + 0.1 * (1 - police_per_capita / 4.0)
            )
            crime_rate = (base_crime / (pop / 100000)) * (1 + crime_influence * np.random.uniform(0.5, 1.5))
            crime_rate = max(100, min(5000, crime_rate))

            rows.append({
                "district": district,
                "state": "Karnataka",
                "year": year,
                "population": pop,
                "population_density": round(density, 2),
                "urbanization_rate": round(urbanization, 3),
                "literacy_rate": round(literacy, 3),
                "avg_income": round(income, 2),
                "poverty_rate": round(poverty, 3),
                "unemployment_rate": round(unemployment, 3),
                "migration_rate": round(migration, 3),
                "juvenile_population_pct": round(juvenile_pct, 3),
                "police_per_capita": round(police_per_capita, 2),
                "crime_rate_per_100k": round(crime_rate, 2),
            })

    return pd.DataFrame(rows)
