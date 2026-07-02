"""Synthetic financial transactions with anomalous patterns."""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

TRANSACTION_TYPES = ["transfer", "withdrawal", "deposit", "payment", "international_transfer"]
CURRENCIES = ["INR", "USD", "EUR", "GBP"]
FRAUD_PATTERNS = ["circular_transfer", "smurfing", "rapid_flow", "high_value_anomaly", "unusual_location"]


def generate_transactions(
    n_normal: int = 5000,
    n_fraud: int = 100,
    seed: int = 42,
) -> pd.DataFrame:
    np.random.seed(seed)
    transactions = []

    base_time = datetime(2024, 1, 1)

    for i in range(n_normal):
        txn_type = np.random.choice(TRANSACTION_TYPES, p=[0.3, 0.2, 0.2, 0.2, 0.1])
        amount = np.random.lognormal(mean=8, sigma=1.5)
        timestamp = base_time + timedelta(
            days=int(np.random.randint(0, 365)),
            hours=int(np.random.randint(6, 23)),
            minutes=int(np.random.randint(0, 60)),
        )
        transactions.append({
            "transaction_id": f"TXN-{i:06d}",
            "amount": round(amount, 2),
            "transaction_type": txn_type,
            "currency": np.random.choice(CURRENCIES, p=[0.7, 0.15, 0.1, 0.05]),
            "sender_account": f"ACC-{np.random.randint(1000, 9999)}",
            "receiver_account": f"ACC-{np.random.randint(1000, 9999)}",
            "timestamp": timestamp,
            "is_fraud": 0,
            "fraud_pattern": None,
        })

    for i in range(n_fraud):
        pattern = np.random.choice(FRAUD_PATTERNS)
        txn_type = np.random.choice(TRANSACTION_TYPES, p=[0.4, 0.1, 0.1, 0.3, 0.1])

        if pattern == "high_value_anomaly":
            amount = np.random.uniform(500000, 5000000)
        elif pattern == "smurfing":
            amount = np.random.uniform(40000, 99000)
        elif pattern == "rapid_flow":
            amount = np.random.uniform(100000, 200000)
        else:
            amount = np.random.uniform(50000, 500000)

        timestamp = base_time + timedelta(
            days=int(np.random.randint(0, 365)),
            hours=int(np.random.choice([1, 2, 3, 4, 22, 23])),
            minutes=int(np.random.randint(0, 60)),
        )

        sender = f"ACC-{np.random.randint(1000, 9999)}"
        receiver = f"ACC-{np.random.randint(1000, 9999)}" if pattern != "circular_transfer" else sender

        transactions.append({
            "transaction_id": f"TXN-FRAUD-{i:04d}",
            "amount": round(amount, 2),
            "transaction_type": txn_type,
            "currency": np.random.choice(CURRENCIES, p=[0.6, 0.2, 0.1, 0.1]),
            "sender_account": sender,
            "receiver_account": receiver,
            "timestamp": timestamp,
            "is_fraud": 1,
            "fraud_pattern": pattern,
        })

    df = pd.DataFrame(transactions)
    df["hour"] = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.dayofweek
    df["is_night"] = (df["hour"] < 6).astype(int)
    df["amount_log"] = np.log1p(df["amount"])

    return df.sample(frac=1, random_state=seed).reset_index(drop=True)
