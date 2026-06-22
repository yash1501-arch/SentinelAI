"""Synthetic case description data for similarity training."""
import numpy as np
import pandas as pd

CASE_TEMPLATES = {
    "theft": [
        "Suspect stole {item} from {location} at {time}. CCTV footage shows {desc}.",
        "Complainant reported missing {item} from {location}. Investigation ongoing.",
        "Burglary at {location}. Perpetrator entered through {entry_point} and stole {item}.",
    ],
    "assault": [
        "Victim was attacked near {location} by {n_suspects} suspects. {desc} injuries reported.",
        "Physical altercation at {location} involving {n_suspects} persons. Weapon used: {weapon}.",
        "Assault and battery case. Victim treated for {desc} injuries at local hospital.",
    ],
    "robbery": [
        "Armed robbery at {location}. Suspects brandished {weapon} and demanded valuables.",
        "Street robbery near {location}. Perpetrator fled on foot with stolen {item}.",
        "Chain snatching incident at {location}. Suspect approached on motorcycle.",
    ],
    "fraud": [
        "Online fraud case. Victim transferred {amount} to fake account purporting to be {entity}.",
        "Identity theft reported. Fraudulent transactions totalling {amount} detected.",
        "Credit card skimming at {location}. {n_suspects} suspects involved in operation.",
    ],
    "homicide": [
        "Homicide investigation at {location}. Victim identified as {victim_desc}.",
        "Suspicious death at {location}. Forensic analysis {forensic_desc}.",
        "Murder case. Body discovered at {location} with {desc} injuries.",
    ],
}

LOCATIONS = ["MG Road", "Indiranagar", "Koramangala", "Whitefield", "Jayanagar",
              "BTM Layout", "Marathahalli", "Electronic City", "Yelahanka", "Rajajinagar"]
ITEMS = ["laptop", "mobile phone", "wallet", "jewelry", "cash", "documents", "bicycle", "motorcycle"]
WEAPONS = ["knife", "gun", "iron rod", "baseball bat", "broken bottle"]
ENTRY_POINTS = ["window", "back door", "main door", "roof"]
DESCS = ["minor", "severe", "critical", "moderate"]
ENTITIES = ["bank", "government agency", "insurance company", "online store"]
VICTIM_DESCS = ["a 35-year-old male", "a 28-year-old female", "a 45-year-old male"]
FORENSIC_DESCS = ["indicates foul play", "inconclusive", "matching suspect DNA found"]


def generate_case_descriptions(n_per_type: int = 20, seed: int = 42) -> pd.DataFrame:
    np.random.seed(seed)
    rows = []

    for _ in range(n_per_type):
        for crime_type, templates in CASE_TEMPLATES.items():
            template = np.random.choice(templates)
            text = template.format(
                location=np.random.choice(LOCATIONS),
                item=np.random.choice(ITEMS),
                time=np.random.choice(["daytime", "night", "evening", "early morning"]),
                desc=np.random.choice(DESCS),
                n_suspects=np.random.randint(1, 4),
                entry_point=np.random.choice(ENTRY_POINTS),
                weapon=np.random.choice(WEAPONS),
                amount=f"Rs. {np.random.randint(1000, 500000)}",
                entity=np.random.choice(ENTITIES),
                victim_desc=np.random.choice(VICTIM_DESCS),
                forensic_desc=np.random.choice(FORENSIC_DESCS),
            )
            rows.append({"case_id": f"CASE-{crime_type}-{_:03d}", "crime_type": crime_type, "description": text})

    return pd.DataFrame(rows)
