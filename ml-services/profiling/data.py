"""Synthetic training data generator for offender profiling."""
import pandas as pd
import numpy as np
from typing import Tuple

OFFENDER_ARCHETYPES = [
    "Opportunistic Offender",
    "Organized Criminal",
    "Violent Predator",
    "Financial Fraudster",
    "Gang Associate",
    "Situational Offender",
]

RISK_LEVELS = ["Low", "Medium", "High", "Critical"]


def generate_dataset(n_samples: int = 5000, seed: int = 42) -> pd.DataFrame:
    np.random.seed(seed)

    age = np.random.normal(35, 12, n_samples).clip(14, 80)
    prior_cases = np.random.poisson(2, n_samples)
    is_repeat = (prior_cases > 0).astype(float) * np.random.binomial(1, 0.6, n_samples)
    education_level = np.random.choice(["none", "primary", "secondary", "graduate", "postgraduate"], n_samples, p=[0.1, 0.2, 0.4, 0.2, 0.1])
    employment = np.random.choice(["unemployed", "employed", "self-employed", "student", "retired"], n_samples, p=[0.3, 0.3, 0.2, 0.1, 0.1])
    gender = np.random.choice(["male", "female"], n_samples, p=[0.85, 0.15])
    substance_abuse = np.random.binomial(1, 0.3, n_samples)
    gang_affiliation = np.random.binomial(1, 0.15, n_samples)
    mental_health = np.random.binomial(1, 0.1, n_samples)
    weapon_use = np.random.binomial(1, 0.25, n_samples)
    violence_score = np.random.beta(2, 5, n_samples)

    edu_map = {"none": 0, "primary": 1, "secondary": 2, "graduate": 3, "postgraduate": 4}
    emp_map = {"unemployed": 0, "employed": 1, "self-employed": 2, "student": 3, "retired": 4}
    gender_map = {"male": 1, "female": 0}

    df = pd.DataFrame({
        "age": age,
        "prior_cases": prior_cases,
        "is_repeat_offender": is_repeat,
        "education_score": [edu_map[e] for e in education_level],
        "employment_score": [emp_map[e] for e in employment],
        "is_male": [gender_map[g] for g in gender],
        "substance_abuse": substance_abuse,
        "gang_affiliation": gang_affiliation,
        "mental_health_issues": mental_health,
        "weapon_use": weapon_use,
        "violence_score": violence_score,
    })

    risk_score = (
        0.15 * (df["age"] < 25).astype(float)
        + 0.2 * (df["prior_cases"] > 2).astype(float)
        + 0.1 * (df["education_score"] < 2).astype(float)
        + 0.1 * df["substance_abuse"]
        + 0.15 * df["gang_affiliation"]
        + 0.1 * df["weapon_use"]
        + 0.2 * df["violence_score"]
        + np.random.normal(0, 0.05, n_samples)
    ).clip(0, 1)

    recidivism_prob = (
        0.3 * df["is_repeat_offender"]
        + 0.2 * (df["age"] < 30).astype(float)
        + 0.15 * (df["education_score"] < 2).astype(float)
        + 0.1 * df["substance_abuse"]
        + 0.15 * df["gang_affiliation"]
        + 0.1 * df["violence_score"]
        + np.random.normal(0, 0.05, n_samples)
    ).clip(0, 1)

    escalation_raw = (
        0.2 * (df["age"] < 25).astype(float)
        + 0.15 * df["prior_cases"]
        + 0.2 * df["weapon_use"]
        + 0.25 * df["violence_score"]
        + 0.2 * df["substance_abuse"]
        + np.random.normal(0, 0.05, n_samples)
    )
    escalation_bins = [0, 0.25, 0.5, 0.75, 1.0]
    escalation_labels = ["Low", "Medium", "High", "Critical"]
    escalation_risk = pd.cut(escalation_raw, bins=escalation_bins, labels=escalation_labels)

    archetype_idx = np.random.choice(range(6), n_samples, p=[0.2, 0.1, 0.15, 0.15, 0.1, 0.3])
    archetype = [OFFENDER_ARCHETYPES[i] for i in archetype_idx]

    df["risk_score"] = risk_score
    df["recidivism_probability"] = recidivism_prob
    df["escalation_risk"] = escalation_risk
    df["archetype"] = archetype

    return df


def split_data(df: pd.DataFrame, test_size: float = 0.2) -> Tuple[pd.DataFrame, pd.DataFrame]:
    n_test = int(len(df) * test_size)
    indices = np.random.permutation(len(df))
    test_idx = indices[:n_test]
    train_idx = indices[n_test:]
    return df.iloc[train_idx].copy(), df.iloc[test_idx].copy()
