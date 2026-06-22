"""Base Neo4j data importer class."""
from neo4j import AsyncGraphDatabase
from typing import AsyncGenerator


class BaseImporter:
    def __init__(self, uri: str, user: str, password: str):
        self._driver = AsyncGraphDatabase.driver(uri, auth=(user, password))

    async def close(self):
        await self._driver.close()

    async def execute_batch(self, cypher: str, records: list[dict], batch_size: int = 500):
        total = len(records)
        for i in range(0, total, batch_size):
            batch = records[i : i + batch_size]
            async with self._driver.session() as session:
                await session.run(
                    f"UNWIND $batch AS row {cypher}",
                    batch=batch,
                )
        return total

    async def clear_database(self):
        async with self._driver.session() as session:
            await session.run("MATCH (n) DETACH DELETE n")

    async def create_constraints(self):
        async with self._driver.session() as session:
            constraints = [
                "CREATE CONSTRAINT IF NOT EXISTS FOR (p:Person) REQUIRE p.id IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Case) REQUIRE c.id IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (g:Gang) REQUIRE g.id IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (l:Location) REQUIRE l.id IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (e:Evidence) REQUIRE e.id IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (f:FIR) REQUIRE f.id IS UNIQUE",
            ]
            for c in constraints:
                await session.run(c)

    async def count_nodes(self) -> dict:
        async with self._driver.session() as session:
            result = await session.run("""
                MATCH (n)
                RETURN labels(n)[0] AS label, count(*) AS count
                ORDER BY count DESC
            """)
            counts = {r["label"]: r["count"] async for r in result}
            result2 = await session.run("MATCH ()-[r]-() RETURN count(r) AS total")
            total_rels = await result2.single()
            counts["_total_relationships"] = total_rels["total"] if total_rels else 0
            return counts
