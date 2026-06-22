# SENTINEL AI — RAG Architecture

## Overview

Retrieval-Augmented Generation (RAG) enables semantic search across crime documents, FIRs, case notes, witness statements, and evidence descriptions using vector embeddings.

## Vector Storage: Qdrant Cloud

### Collections

| Collection Name | Vector Dim | Documents Indexed |
|----------------|-----------|------------------|
| crime_descriptions | 384 | Crime incident descriptions |
| fir_text | 384 | FIR brief facts |
| case_notes | 384 | Investigation notes |
| witness_statements | 384 | Witness statements |
| evidence_descriptions | 384 | Evidence descriptions |

### Document Chunking Strategy

```python
CHUNK_SIZE = 500   # characters
CHUNK_OVERLAP = 50 # characters
```

### Metadata Stored Per Point

```json
{
    "document_id": "UUID",
    "document_type": "fir|case_note|evidence|witness_statement",
    "fir_number": "string",
    "case_id": "UUID",
    "district": "string",
    "crime_type": "string",
    "created_at": "timestamp",
    "source_url": "string",
    "chunk_index": "int"
}
```

## Embedding Pipeline

```
┌─────────────┐    ┌──────────────┐    ┌──────────────┐
│  PostgreSQL  │───▶│  Sentence    │───▶│   Qdrant     │
│  (Source)    │    │ Transformer  │    │   (Index)    │
└─────────────┘    └──────────────┘    └──────────────┘
                         │
                    Model: all-MiniLM-L6-v2
                    Dim: 384
                    Distance: Cosine
```

### Ingestion Flow
1. Read new/updated records from DataStore
2. Chunk text fields into 500-char segments
3. Generate embeddings via Sentence Transformers
4. Upsert to Qdrant with metadata and payload
5. Scheduler runs every 15 minutes for sync

## Retrieval Flow

```
┌──────────┐    ┌──────────────┐    ┌──────────────┐
│ User     │───▶│  Embed Query  │───▶│  Qdrant      │
│ Query    │    │  (ST Model)   │    │  Search      │
└──────────┘    └──────────────┘    └──────────────┘
                                          │
                                    ┌─────▼──────┐
                                    │  Rank by    │
                                    │  Cosine     │
                                    │  Similarity │
                                    └─────┬──────┘
                                          │
                                    ┌─────▼──────┐
                                    │  Format as  │
                                    │  Context    │
                                    │  for LLM    │
                                    └─────┬──────┘
                                          │
                                    ┌─────▼──────┐
                                    │  Generate   │
                                    │  Response   │
                                    │  + Sources  │
                                    └────────────┘
```

### Filtering
Support filtered search by:
- `district` — Location-based filtering
- `crime_type` — Crime category filter
- `date_range` — Temporal filtering
- `document_type` — Source type filter

## Similar Case Retrieval

```python
def find_similar_cases(case_id: UUID, top_k: int = 10):
    # 1. Get embedding of source case
    source_embedding = get_case_embedding(case_id)

    # 2. Search Qdrant with filter excluding self
    results = qdrant.search(
        collection="crime_descriptions",
        vector=source_embedding,
        top_k=top_k + 1,
        filter={"must_not": {"id": case_id}}
    )

    # 3. Return top-k with scores and metadata
    return [
        {
            "case_id": r.payload["case_id"],
            "fir_number": r.payload["fir_number"],
            "crime_type": r.payload["crime_type"],
            "similarity_score": r.score,
            "matched_features": extract_matched_features(r),
        }
        for r in results[:top_k]
    ]
```

## Performance Targets

| Metric | Target |
|--------|--------|
| Embedding latency | < 100ms per document |
| Search latency (p95) | < 200ms |
| Recall@10 | > 0.85 |
| Index freshness | < 15 minutes |
