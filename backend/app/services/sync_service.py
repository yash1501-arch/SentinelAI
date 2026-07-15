"""
Data synchronization service for SentinelAI.

Handles syncing PostgreSQL data to Neo4j and Qdrant on a scheduled basis.
Can be triggered via Catalyst Scheduler or manually via admin endpoint.
"""
from datetime import datetime, timezone
from loguru import logger

from app.core.database import async_session_factory
from sqlalchemy import text


class Neo4jSyncService:
    """Syncs crime data from PostgreSQL to Neo4j graph database."""

    @classmethod
    async def sync_persons(cls) -> dict:
        """Sync person nodes to Neo4j."""
        try:
            from app.services.neo4j_service import Neo4jService

            async with async_session_factory() as session:
                # Get persons updated in last sync window (15 min)
                result = await session.execute(text("""
                    SELECT id, first_name, last_name, gender, phone, occupation,
                           education_level, date_of_birth
                    FROM persons
                    WHERE updated_at >= NOW() - INTERVAL '15 minutes'
                    LIMIT 100
                """))
                persons = [dict(row._mapping) for row in result]

            synced = 0
            for person in persons:
                try:
                    await Neo4jService.run_query("""
                        MERGE (p:Person {id: $id})
                        SET p.first_name = $first_name,
                            p.last_name = $last_name,
                            p.gender = $gender,
                            p.phone = $phone,
                            p.occupation = $occupation,
                            p.updated_at = datetime()
                    """, {
                        "id": str(person["id"]),
                        "first_name": person["first_name"],
                        "last_name": person["last_name"],
                        "gender": str(person.get("gender", "")),
                        "phone": person.get("phone", ""),
                        "occupation": person.get("occupation", ""),
                    })
                    synced += 1
                except Exception as e:
                    logger.error(f"Failed to sync person {person['id']}: {e}")

            return {"persons_synced": synced, "total_found": len(persons)}

        except Exception as e:
            logger.error(f"Person sync error: {e}")
            return {"persons_synced": 0, "error": str(e)}

    @classmethod
    async def sync_crimes(cls) -> dict:
        """Sync crime incident nodes to Neo4j."""
        try:
            from app.services.neo4j_service import Neo4jService

            async with async_session_factory() as session:
                result = await session.execute(text("""
                    SELECT ci.id, f.fir_number, ci.incident_date, ct.name as crime_type,
                           ci.description, ci.is_solved
                    FROM crime_incidents ci
                    JOIN firs f ON ci.fir_id = f.id
                    JOIN crime_types ct ON ci.crime_type_id = ct.id
                    WHERE ci.updated_at >= NOW() - INTERVAL '15 minutes'
                    LIMIT 100
                """))
                crimes = [dict(row._mapping) for row in result]

            synced = 0
            for crime in crimes:
                try:
                    await Neo4jService.run_query("""
                        MERGE (c:Crime {id: $id})
                        SET c.fir_number = $fir_number,
                            c.incident_date = $incident_date,
                            c.crime_type = $crime_type,
                            c.is_solved = $is_solved,
                            c.updated_at = datetime()
                    """, {
                        "id": str(crime["id"]),
                        "fir_number": crime["fir_number"],
                        "incident_date": str(crime["incident_date"]),
                        "crime_type": crime["crime_type"],
                        "is_solved": crime["is_solved"],
                    })
                    synced += 1
                except Exception as e:
                    logger.error(f"Failed to sync crime {crime['id']}: {e}")

            return {"crimes_synced": synced, "total_found": len(crimes)}

        except Exception as e:
            logger.error(f"Crime sync error: {e}")
            return {"crimes_synced": 0, "error": str(e)}

    @classmethod
    async def sync_relationships(cls) -> dict:
        """Sync person-crime relationships (PARTICIPATED_IN) to Neo4j."""
        try:
            from app.services.neo4j_service import Neo4jService

            async with async_session_factory() as session:
                # Sync accused relationships
                result = await session.execute(text("""
                    SELECT a.person_id, a.incident_id, 'accused' as role
                    FROM accused a
                    WHERE a.created_at >= NOW() - INTERVAL '15 minutes'
                    LIMIT 100
                """))
                relationships = [dict(row._mapping) for row in result]

            synced = 0
            for rel in relationships:
                try:
                    await Neo4jService.run_query("""
                        MATCH (p:Person {id: $person_id})
                        MATCH (c:Crime {id: $crime_id})
                        MERGE (p)-[r:PARTICIPATED_IN]->(c)
                        SET r.role = $role
                    """, {
                        "person_id": str(rel["person_id"]),
                        "crime_id": str(rel["incident_id"]),
                        "role": rel["role"],
                    })
                    synced += 1
                except Exception as e:
                    logger.error(f"Failed to sync relationship: {e}")

            return {"relationships_synced": synced, "total_found": len(relationships)}

        except Exception as e:
            logger.error(f"Relationship sync error: {e}")
            return {"relationships_synced": 0, "error": str(e)}

    @classmethod
    async def full_sync(cls) -> dict:
        """Run full sync of persons, crimes, and relationships."""
        logger.info("Starting Neo4j full sync...")
        persons = await cls.sync_persons()
        crimes = await cls.sync_crimes()
        relationships = await cls.sync_relationships()

        result = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **persons,
            **crimes,
            **relationships,
        }
        logger.info(f"Neo4j sync complete: {result}")
        return result


class EmbeddingSyncService:
    """Syncs new crime data to Qdrant vector database."""

    @classmethod
    async def sync_embeddings(cls) -> dict:
        """Generate embeddings for new records and upsert to Qdrant."""
        try:
            from app.services.qdrant_service import QdrantService
            from app.services.embedding_service import EmbeddingService

            async with async_session_factory() as session:
                # Get recent crime descriptions
                result = await session.execute(text("""
                    SELECT ci.id, ci.description, ci.modus_operandi,
                           ct.name as crime_type, f.district, f.fir_number
                    FROM crime_incidents ci
                    JOIN crime_types ct ON ci.crime_type_id = ct.id
                    JOIN firs f ON ci.fir_id = f.id
                    WHERE ci.updated_at >= NOW() - INTERVAL '15 minutes'
                    LIMIT 50
                """))
                records = [dict(row._mapping) for row in result]

            if not records:
                return {"documents_processed": 0, "message": "No new records to sync"}

            # Generate embeddings
            texts = [
                f"{r['crime_type']}: {r['description']} {r.get('modus_operandi', '')}"
                for r in records
            ]

            embeddings = await EmbeddingService.embed_texts(texts)

            # Upsert to Qdrant
            points = []
            for i, record in enumerate(records):
                points.append({
                    "id": str(record["id"]),
                    "vector": embeddings[i],
                    "payload": {
                        "case_id": str(record["id"]),
                        "fir_number": record["fir_number"],
                        "crime_type": record["crime_type"],
                        "district": record["district"],
                        "document_type": "crime_description",
                    },
                })

            await QdrantService.upsert_points("crime_descriptions", points)

            return {
                "documents_processed": len(records),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            logger.error(f"Embedding sync error: {e}")
            return {"documents_processed": 0, "error": str(e)}
