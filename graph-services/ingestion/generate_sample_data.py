"""Synthetic data generator that creates CSV files matching the import schema."""
import csv
import uuid
import random
import os
from datetime import datetime, timedelta
from typing import Optional


def generate_persons_csv(path: str, n: int = 100):
    FIRST = ["Rajesh", "Suresh", "Mahesh", "Ramesh", "Ravi", "Vijay", "Ajay", "Sanjay",
             "Anita", "Sunita", "Geeta", "Neha", "Priya", "Kavita", "Shwetha", "Lakshmi"]
    LAST = ["Kumar", "Singh", "Reddy", "Patil", "Nair", "Iyer", "Joshi", "Shetty",
            "Naik", "Hegde", "Rao", "Murthy", "Desai", "Pillai"]
    OCCUPATIONS = ["unemployed", "laborer", "driver", "shopkeeper", "student", "farmer",
                    "private_employee", "govt_employee", "professional", "business"]

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "id", "first_name", "last_name", "phone", "gender",
            "date_of_birth", "occupation", "aadhaar_number",
        ])
        writer.writeheader()
        for _ in range(n):
            gender = random.choice(["male", "female"])
            dob = datetime.now() - timedelta(days=random.randint(6570, 29200))
            writer.writerow({
                "id": str(uuid.uuid4()),
                "first_name": random.choice(FIRST),
                "last_name": random.choice(LAST),
                "phone": f"+91{random.randint(6000000000, 9999999999)}",
                "gender": gender,
                "date_of_birth": dob.strftime("%Y-%m-%d"),
                "occupation": random.choice(OCCUPATIONS),
                "aadhaar_number": str(random.randint(100000000000, 999999999999)),
            })
    print(f"Wrote {n} persons to {path}")


def generate_cases_csv(path: str, n: int = 50):
    CRIME_TYPES = ["theft", "assault", "robbery", "burglary", "homicide", "fraud", "kidnapping", "dacoity"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "id", "fir_number", "description", "incident_date",
            "crime_type", "is_solved", "severity",
        ])
        writer.writeheader()
        for i in range(n):
            date = datetime.now() - timedelta(days=random.randint(0, 365))
            writer.writerow({
                "id": str(uuid.uuid4()),
                "fir_number": f"FIR-{2024}-{i+1:04d}",
                "description": f"Case involving {random.choice(CRIME_TYPES)} at unknown location",
                "incident_date": date.strftime("%Y-%m-%d"),
                "crime_type": random.choice(CRIME_TYPES),
                "is_solved": str(random.random() > 0.6).lower(),
                "severity": random.choice(["standard", "heinous", "critical"]),
            })
    print(f"Wrote {n} cases to {path}")


def generate_locations_csv(path: str, case_ids: list[str]):
    DISTRICTS = ["Bengaluru Urban", "Bengaluru Rural", "Mysuru", "Hubli", "Mangaluru"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "id", "case_id", "latitude", "longitude", "address", "district", "city",
        ])
        writer.writeheader()
        for cid in case_ids:
            writer.writerow({
                "id": str(uuid.uuid4()),
                "case_id": cid,
                "latitude": round(12.97 + random.uniform(-0.1, 0.1), 6),
                "longitude": round(77.59 + random.uniform(-0.1, 0.1), 6),
                "address": f"{random.randint(1, 999)}, {random.choice(['MG Road', 'Indiranagar', 'Koramangala', 'Whitefield'])}",
                "district": random.choice(DISTRICTS),
                "city": "Bengaluru",
            })
    print(f"Wrote {len(case_ids)} locations to {path}")


def generate_evidence_csv(path: str, case_ids: list[str]):
    EVIDENCE_TYPES = ["forensic", "digital", "document", "physical", "testimony", "cctv"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "id", "case_id", "name", "evidence_type", "description",
        ])
        writer.writeheader()
        for cid in case_ids:
            for _ in range(random.randint(1, 4)):
                writer.writerow({
                    "id": str(uuid.uuid4()),
                    "case_id": cid,
                    "name": f"Evidence-{random.randint(100, 999)}",
                    "evidence_type": random.choice(EVIDENCE_TYPES),
                    "description": f"Collected during investigation of case {cid[:8]}",
                })
    print(f"Generated evidence records to {path}")


def generate_all(output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    generate_persons_csv(os.path.join(output_dir, "persons.csv"), 100)
    generate_cases_csv(os.path.join(output_dir, "cases.csv"), 50)

    import pandas as pd
    cases = pd.read_csv(os.path.join(output_dir, "cases.csv"))
    case_ids = cases["id"].tolist()

    generate_locations_csv(os.path.join(output_dir, "locations.csv"), case_ids)
    generate_evidence_csv(os.path.join(output_dir, "evidence.csv"), case_ids)
    print(f"\nAll CSV files generated in {output_dir}")


if __name__ == "__main__":
    generate_all("./sample_data")
