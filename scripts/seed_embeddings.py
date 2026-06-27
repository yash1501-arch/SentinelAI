"""
Seed Qdrant vector database with crime description embeddings.

Run this script after the database is seeded to populate Qdrant
with searchable embeddings for RAG queries.

Usage:
    python scripts/seed_embeddings.py
"""
import sys
import asyncio
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.core.config import settings
from app.core.database import async_session_factory, init_db
from app.services.embedding_service import EmbeddingService
from sqlalchemy import text


async def seed_embeddings():
    """Generate and upsert embeddings for all crime descriptions."""
    from qdrant_client import QdrantClient
    from qdrant_client.models import PointStruct, VectorParams, Distance

    print(f"Connecting to Qdrant at {settings.QDRANT_URL}...")
    client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY or None)

    # Ensure collections exist
    collections = client.get_collections().collections
    existing = {c.name for c in collections}

    COLLECTIONS = ["crime_descriptions", "fir_text", "case_notes"]
    for name in COLLECTIONS:
        if name not in existing:
            client.create_collection(
                collection_name=name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE),
            )
            print(f"  Created collection: {name}")

    # Initialize DB
    await init_db()

    # Fetch crime descriptions
    async with async_session_factory() as session:
        result = await session.execute(text("""
            SELECT ci.id, ci.description, ci.modus_operandi,
                   ct.name as crime_type, ct.category,
                   f.district, f.fir_number, f.police_station
            FROM crime_incidents ci
            JOIN crime_types ct ON ci.crime_type_id = ct.id
            JOIN firs f ON ci.fir_id = f.id
            ORDER BY ci.created_at DESC
            LIMIT 200
        """))
        records = [dict(row._mapping) for row in result]

    if not records:
        print("No crime records found in database. Run the backend first to seed data.")
        return

    print(f"Found {len(records)} crime records. Generating embeddings...")

    # Generate embeddings for crime descriptions
    texts = [
        f"{r['crime_type']} ({r['category']}): {r['description']} "
        f"{'Modus operandi: ' + r['modus_operandi'] if r.get('modus_operandi') else ''}"
        for r in records
    ]
    embeddings = EmbeddingService.embed_texts(texts)

    # Upsert to crime_descriptions collection
    points = []
    for i, record in enumerate(records):
        points.append(PointStruct(
            id=i,
            vector=embeddings[i],
            payload={
                "case_id": str(record["id"]),
                "fir_number": record["fir_number"],
                "crime_type": record["crime_type"],
                "category": record["category"],
                "district": record["district"],
                "police_station": record["police_station"],
                "document_type": "crime_description",
                "text_preview": texts[i][:200],
            },
        ))

    client.upsert(collection_name="crime_descriptions", points=points)
    print(f"  Upserted {len(points)} points to 'crime_descriptions'")

    # Generate embeddings for FIR brief facts
    async with async_session_factory() as session:
        result = await session.execute(text("""
            SELECT id, fir_number, brief_fact, district, police_station
            FROM firs
            ORDER BY created_at DESC
            LIMIT 200
        """))
        firs = [dict(row._mapping) for row in result]

    if firs:
        fir_texts = [f"FIR {r['fir_number']}: {r['brief_fact']}" for r in firs]
        fir_embeddings = EmbeddingService.embed_texts(fir_texts)

        fir_points = []
        for i, record in enumerate(firs):
            fir_points.append(PointStruct(
                id=i,
                vector=fir_embeddings[i],
                payload={
                    "fir_number": record["fir_number"],
                    "district": record["district"],
                    "police_station": record["police_station"],
                    "document_type": "fir_text",
                    "text_preview": fir_texts[i][:200],
                },
            ))

        client.upsert(collection_name="fir_text", points=fir_points)
        print(f"  Upserted {len(fir_points)} points to 'fir_text'")

    # Summary
    for name in COLLECTIONS:
        info = client.get_collection(name)
        print(f"  Collection '{name}': {info.points_count} points")

    print("\nEmbedding seeding complete!")


if __name__ == "__main__":
    asyncio.run(seed_embeddings())
