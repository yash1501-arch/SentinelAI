"""Semantic case similarity using Sentence Transformers + cosine similarity."""
import os
import json
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import joblib

from .data import generate_case_descriptions

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODELS_DIR, exist_ok=True)

EMBEDDING_MODEL = "all-MiniLM-L6-v2"


def build_index(save: bool = True) -> dict:
    df = generate_case_descriptions(50)
    texts = df["description"].tolist()
    case_ids = df["case_id"].tolist()

    encoder = SentenceTransformer(EMBEDDING_MODEL)
    embeddings = encoder.encode(texts, show_progress_bar=True, normalize_embeddings=True)

    {
        "case_ids": case_ids,
        "crime_types": df["crime_type"].tolist(),
        "descriptions": texts,
        "embeddings": embeddings,
    }

    if save:
        os.makedirs(MODELS_DIR, exist_ok=True)
        joblib.dump({"model_name": EMBEDDING_MODEL}, os.path.join(MODELS_DIR, "encoder.pkl"))
        np.save(os.path.join(MODELS_DIR, "embeddings.npy"), embeddings)
        pd.DataFrame({"case_id": case_ids, "crime_type": df["crime_type"], "description": texts}).to_csv(
            os.path.join(MODELS_DIR, "cases.csv"), index=False
        )
        print(f"Index saved to {MODELS_DIR}")

    sim_matrix = cosine_similarity(embeddings)
    n_total = len(case_ids)
    (n_total * (n_total - 1)) // 2

    return {
        "n_cases": n_total,
        "embedding_dim": embeddings.shape[1],
        "model": EMBEDDING_MODEL,
        "avg_similarity": round(float(np.mean(sim_matrix[sim_matrix < 0.99])), 4),
        "case_types": df["crime_type"].value_counts().to_dict(),
    }


def search(query: str, top_k: int = 5) -> list:
    try:
        metadata = joblib.load(os.path.join(MODELS_DIR, "encoder.pkl"))
        model_name = metadata.get("model_name", EMBEDDING_MODEL) if isinstance(metadata, dict) else EMBEDDING_MODEL
    except Exception:
        model_name = EMBEDDING_MODEL

    encoder = SentenceTransformer(model_name)
    embeddings = np.load(os.path.join(MODELS_DIR, "embeddings.npy"))
    cases = pd.read_csv(os.path.join(MODELS_DIR, "cases.csv"))

    query_emb = encoder.encode([query], normalize_embeddings=True)
    scores = cosine_similarity(query_emb, embeddings)[0]
    top_indices = scores.argsort()[-top_k:][::-1]

    return [
        {
            "case_id": cases.iloc[i]["case_id"],
            "crime_type": cases.iloc[i]["crime_type"],
            "description": cases.iloc[i]["description"][:120],
            "similarity_score": round(float(scores[i]), 4),
        }
        for i in top_indices if scores[i] > 0.3
    ]


if __name__ == "__main__":
    stats = build_index()
    print(json.dumps(stats, indent=2))
