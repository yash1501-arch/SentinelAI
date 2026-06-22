"""Cypher query execution utility wrapping the Neo4j async driver."""
from neo4j import AsyncGraphDatabase


class CypherExecutor:
    def __init__(self, uri: str, user: str, password: str):
        self._driver = AsyncGraphDatabase.driver(uri, auth=(user, password))

    async def close(self):
        await self._driver.close()

    async def run(self, query: str, params: dict = None) -> list[dict]:
        async with self._driver.session() as session:
            result = await session.run(query, params or {})
            return [dict(r) async for r in result]

    async def run_query(self, query_name: str, params: dict = None) -> list[dict]:
        from .queries import QUERIES
        query = QUERIES.get(query_name)
        if not query:
            raise ValueError(f"Unknown query: {query_name}. Available: {list(QUERIES.keys())}")
        return await self.run(query, params)

    async def execute_transaction(self, queries: list[tuple[str, dict]]) -> list[list[dict]]:
        async with self._driver.session() as session:
            results = []
            for query, params in queries:
                result = await session.run(query, params)
                results.append([dict(r) async for r in result])
            return results

    async def create_indexes(self):
        async with self._driver.session() as session:
            indexes = [
                "CREATE INDEX IF NOT EXISTS FOR (p:Person) ON (p.id)",
                "CREATE INDEX IF NOT EXISTS FOR (p:Person) ON (p.phone)",
                "CREATE INDEX IF NOT EXISTS FOR (p:Person) ON (p.aadhaar_number)",
                "CREATE INDEX IF NOT EXISTS FOR (c:Case) ON (c.id)",
                "CREATE INDEX IF NOT EXISTS FOR (c:Case) ON (c.fir_number)",
                "CREATE INDEX IF NOT EXISTS FOR (g:Gang) ON (g.id)",
                "CREATE INDEX IF NOT EXISTS FOR (l:Location) ON (l.id)",
                "CREATE INDEX IF NOT EXISTS FOR (e:Evidence) ON (e.id)",
            ]
            for idx in indexes:
                await session.run(idx)
