from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import (
    Distance, VectorParams, PointStruct,
    Filter, FieldCondition, MatchValue,
)
from app.core.config import settings
from loguru import logger
from typing import List, Dict, Any, Optional


QDRANT_COLLECTIONS = {
    "crime_descriptions": {"size": 384, "description": "Crime incident descriptions"},
    "fir_text": {"size": 384, "description": "FIR text content"},
    "case_notes": {"size": 384, "description": "Investigation case notes"},
    "witness_statements": {"size": 384, "description": "Witness statements"},
    "evidence_descriptions": {"size": 384, "description": "Evidence descriptions"},
}


class QdrantService:
    _client: AsyncQdrantClient = None

    @classmethod
    def get_client(cls) -> AsyncQdrantClient:
        if cls._client is None:
            cls._client = AsyncQdrantClient(
                url=settings.QDRANT_URL,
                api_key=settings.QDRANT_API_KEY or None,
            )
        return cls._client

    @classmethod
    async def initialize_collections(cls):
        client = cls.get_client()
        for name, config in QDRANT_COLLECTIONS.items():
            collections = await client.get_collections()
            existing = {c.name for c in collections.collections}
            if name not in existing:
                await client.create_collection(
                    collection_name=name,
                    vectors_config=VectorParams(
                        size=config["size"],
                        distance=Distance.COSINE,
                    ),
                )
                logger.info(f"Created Qdrant collection: {name}")

    @classmethod
    async def upsert_points(
        cls,
        collection: str,
        points: List[PointStruct],
    ):
        client = cls.get_client()
        await client.upsert(
            collection_name=collection,
            points=points,
        )

    @classmethod
    async def search_similar(
        cls,
        collection: str,
        query_vector: List[float],
        top_k: int = 10,
        score_threshold: float = 0.7,
        filter_params: Optional[Dict] = None,
    ) -> List[Dict[str, Any]]:
        client = cls.get_client()
        search_filter = None
        if filter_params:
            conditions = []
            for key, value in filter_params.items():
                conditions.append(
                    FieldCondition(
                        key=key,
                        match=MatchValue(value=value),
                    )
                )
            search_filter = Filter(must=conditions)

        results = await client.query_points(
            collection_name=collection,
            query=query_vector,
            limit=top_k,
            score_threshold=score_threshold,
            query_filter=search_filter,
        )
        return [
            {
                "id": str(r.id),
                "score": r.score,
                "payload": r.payload,
            }
            for r in results.points
        ]

    @classmethod
    async def delete_points(cls, collection: str, point_ids: List[str]):
        client = cls.get_client()
        await client.delete(
            collection_name=collection,
            points_selector=point_ids,
        )

    @classmethod
    async def collection_info(cls, collection: str) -> dict:
        client = cls.get_client()
        info = await client.get_collection(collection)
        return {
            "name": collection,
            "status": info.status,
            "vectors_count": info.vectors_count,
            "points_count": info.points_count,
        }
