"""
Set up Neo4j Graph Data Science (GDS) projections.

Creates the 'crime-graph' projection needed for PageRank,
community detection, centrality, and other GDS algorithms.

Usage:
    python scripts/setup_neo4j_gds.py
"""
import sys
import asyncio
import os
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(BACKEND_DIR))
os.chdir(str(BACKEND_DIR))

from app.core.config import settings


async def setup_gds():
    """Create GDS graph projection for analytics."""
    from neo4j import AsyncGraphDatabase

    print(f"Connecting to Neo4j at {settings.NEO4J_URI}...")
    driver = AsyncGraphDatabase.driver(
        settings.NEO4J_URI,
        auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
    )

    try:
        async with driver.session() as session:
            # Check if GDS is available
            try:
                result = await session.run("RETURN gds.version() AS version")
                record = await result.single()
                if record:
                    print(f"  GDS version: {record['version']}")
            except Exception:
                print("  WARNING: Neo4j GDS plugin not available. Graph analytics will use native Cypher fallbacks.")
                print("  Install GDS plugin or use Neo4j Aura Professional for GDS support.")
                return

            # Drop existing projection if it exists
            try:
                await session.run("CALL gds.graph.drop('crime-graph', false)")
                print("  Dropped existing 'crime-graph' projection")
            except Exception:
                pass

            # Create graph projection with all relevant node types and relationships
            create_projection = """
            CALL gds.graph.project(
                'crime-graph',
                ['Person', 'Crime', 'Gang', 'Location', 'BankAccount'],
                {
                    KNOWS: {orientation: 'UNDIRECTED'},
                    PARTICIPATED_IN: {orientation: 'UNDIRECTED'},
                    MEMBER_OF_GANG: {orientation: 'UNDIRECTED'},
                    MEMBER_OF: {orientation: 'UNDIRECTED'},
                    OCCURRED_AT: {orientation: 'UNDIRECTED'},
                    TRANSFERRED_TO: {orientation: 'NATURAL'},
                    FINANCIAL_LINK: {orientation: 'UNDIRECTED'}
                }
            )
            YIELD graphName, nodeCount, relationshipCount
            RETURN graphName, nodeCount, relationshipCount
            """

            try:
                result = await session.run(create_projection)
                record = await result.single()
                if record:
                    print(f"  Created projection: {record['graphName']}")
                    print(f"    Nodes: {record['nodeCount']}")
                    print(f"    Relationships: {record['relationshipCount']}")
            except Exception as e:
                print(f"  Could not create projection: {e}")
                print("  This is normal if the graph has no data yet.")
                print("  Run this script again after syncing data to Neo4j.")

            # Create constraints for uniqueness
            constraints = [
                "CREATE CONSTRAINT IF NOT EXISTS FOR (p:Person) REQUIRE p.id IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Crime) REQUIRE c.id IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (g:Gang) REQUIRE g.id IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (l:Location) REQUIRE l.id IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (b:BankAccount) REQUIRE b.id IS UNIQUE",
            ]

            for c in constraints:
                try:
                    await session.run(c)
                except Exception:
                    pass
            print("  Constraints created/verified")

            # Show node counts
            result = await session.run("""
                MATCH (n)
                RETURN labels(n)[0] AS label, count(*) AS count
                ORDER BY count DESC
            """)
            records = [record async for record in result]
            if records:
                print("\n  Node counts:")
                for r in records:
                    print(f"    {r['label']}: {r['count']}")
            else:
                print("\n  No nodes in graph yet. Sync data first via:")
                print("    POST /api/v1/catalyst/sync/neo4j")

    finally:
        await driver.close()

    print("\nNeo4j GDS setup complete!")


if __name__ == "__main__":
    asyncio.run(setup_gds())
