"""Graph analytics operations executed against Neo4j via the driver."""
from neo4j import AsyncGraphDatabase, AsyncSession
from typing import Optional


class GraphAnalytics:
    def __init__(self, uri: str, user: str, password: str):
        self._driver = AsyncGraphDatabase.driver(uri, auth=(user, password))

    async def close(self):
        await self._driver.close()

    async def page_rank(self, top_n: int = 20) -> list[dict]:
        async with self._driver.session() as session:
            result = await session.run("""
                CALL gds.pageRank.stream('crime-graph')
                YIELD nodeId, score
                RETURN gds.util.asNode(nodeId).id AS entity_id,
                       labels(gds.util.asNode(nodeId))[0] AS entity_type,
                       gds.util.asNode(nodeId).name AS name,
                       score
                ORDER BY score DESC
                LIMIT $top_n
            """, top_n=top_n)
            return [dict(r) async for r in result]

    async def betweenness_centrality(self, top_n: int = 20) -> list[dict]:
        async with self._driver.session() as session:
            result = await session.run("""
                CALL gds.betweenness.stream('crime-graph')
                YIELD nodeId, score
                RETURN gds.util.asNode(nodeId).id AS entity_id,
                       labels(gds.util.asNode(nodeId))[0] AS entity_type,
                       gds.util.asNode(nodeId).name AS name,
                       score
                ORDER BY score DESC
                LIMIT $top_n
            """, top_n=top_n)
            return [dict(r) async for r in result]

    async def community_detection_lpa(self) -> list[dict]:
        async with self._driver.session() as session:
            result = await session.run("""
                CALL gds.labelPropagation.stream('crime-graph')
                YIELD nodeId, communityId
                RETURN communityId,
                       collect(gds.util.asNode(nodeId).id) AS members,
                       count(*) AS size
                ORDER BY size DESC
            """)
            return [dict(r) async for r in result]

    async def detect_communities_wcc(self) -> list[dict]:
        async with self._driver.session() as session:
            result = await session.run("""
                CALL gds.wcc.stream('crime-graph')
                YIELD nodeId, componentId
                RETURN componentId,
                       collect(gds.util.asNode(nodeId).id) AS members,
                       count(*) AS size
                ORDER BY size DESC
            """)
            return [dict(r) async for r in result]

    async def shortest_path(self, source_id: str, target_id: str, max_depth: int = 6) -> list[dict]:
        async with self._driver.session() as session:
            result = await session.run("""
                MATCH (source {id: $source_id}), (target {id: $target_id})
                CALL gds.shortestPath.dijkstra.stream('crime-graph', {
                    sourceNode: source,
                    targetNode: target,
                    relationshipWeightProperty: 'weight'
                })
                YIELD index, sourceNode, targetNode, totalCost, nodeIds, costs, path
                RETURN index,
                       [nodeId IN nodeIds | gds.util.asNode(nodeId).id] AS node_sequence,
                       totalCost AS total_weight
                ORDER BY index
            """, source_id=source_id, target_id=target_id)
            return [dict(r) async for r in result]

    async def node_similarity(self, node_id: str, top_n: int = 10) -> list[dict]:
        async with self._driver.session() as session:
            result = await session.run("""
                MATCH (target {id: $node_id})
                CALL gds.nodeSimilarity.stream('crime-graph')
                YIELD node1, node2, similarity
                WHERE node1 = target OR node2 = target
                RETURN CASE
                    WHEN node1 = target THEN gds.util.asNode(node2).id
                    ELSE gds.util.asNode(node1).id
                END AS similar_node_id,
                       similarity
                ORDER BY similarity DESC
                LIMIT $top_n
            """, node_id=node_id, top_n=top_n)
            return [dict(r) async for r in result]

    async def triangle_count(self) -> dict:
        async with self._driver.session() as session:
            result = await session.run("""
                CALL gds.triangles('crime-graph')
                YIELD nodeId, triangleCount
                RETURN sum(triangleCount) / 3 AS total_triangles,
                       max(triangleCount) AS max_triangles_for_node
            """)
            return dict(await result.single())

    async def graph_density(self) -> dict:
        async with self._driver.session() as session:
            stats = await session.run("""
                CALL gds.graph.list('crime-graph')
                YIELD nodeCount, relationshipCount
                RETURN nodeCount, relationshipCount
            """)
            row = await stats.single()
            if row:
                n, e = row["nodeCount"], row["relationshipCount"]
                max_edges = n * (n - 1)
                density = e / max_edges if max_edges > 0 else 0
                return {"node_count": n, "edge_count": e, "density": round(density, 6)}
            return {}

    async def degree_distribution(self) -> list[dict]:
        async with self._driver.session() as session:
            result = await session.run("""
                MATCH (n)
                OPTIONAL MATCH (n)-[r]-()
                RETURN n.id AS node_id,
                       labels(n)[0] AS node_type,
                       count(r) AS degree
                ORDER BY degree DESC
            """)
            return [dict(r) async for r in result]

    async def suspicious_patterns(self) -> dict:
        async with self._driver.session() as session:
            isolates = await session.run("""
                MATCH (p:Person)
                WHERE NOT (p)-[:KNOWN|MEMBER_OF|CO_CONSPIRATOR]-()
                RETURN count(p) AS isolated_persons
            """)
            high_degree = await session.run("""
                MATCH (p:Person)-[r]-()
                WITH p, count(r) AS degree
                WHERE degree > 10
                RETURN p.id AS person_id, degree
                ORDER BY degree DESC
            """)
            return {
                "isolated_persons": dict(await isolates.single()),
                "high_degree_persons": [dict(r) async for r in high_degree],
            }
