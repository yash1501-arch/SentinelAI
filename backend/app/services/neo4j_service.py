from neo4j import AsyncGraphDatabase, AsyncDriver
from app.core.config import settings
from loguru import logger


class Neo4jService:
    _driver: AsyncDriver = None

    @classmethod
    async def get_driver(cls) -> AsyncDriver:
        if cls._driver is None:
            cls._driver = AsyncGraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
            )
            logger.info("Neo4j driver initialized")
        return cls._driver

    @classmethod
    async def close(cls):
        if cls._driver:
            await cls._driver.close()
            cls._driver = None
            logger.info("Neo4j driver closed")

    @classmethod
    async def run_query(cls, query: str, params: dict = None) -> list:
        driver = await cls.get_driver()
        async with driver.session(database="neo4j") as session:
            result = await session.run(query, params or {})
            return [record.data() for record in await result.fetch()]

    @classmethod
    async def create_person_node(cls, person_data: dict):
        query = """
        MERGE (p:Person {id: $id})
        SET p.first_name = $first_name,
            p.last_name = $last_name,
            p.gender = $gender,
            p.phone = $phone,
            p.updated_at = timestamp()
        """
        await cls.run_query(query, person_data)

    @classmethod
    async def create_crime_node(cls, crime_data: dict):
        query = """
        MERGE (c:Crime {id: $id})
        SET c.fir_number = $fir_number,
            c.incident_date = $incident_date,
            c.crime_type = $crime_type,
            c.category = $category,
            c.district = $district,
            c.description = $description,
            c.is_solved = $is_solved,
            c.updated_at = timestamp()
        """
        await cls.run_query(query, crime_data)

    @classmethod
    async def link_person_to_crime(cls, person_id: str, crime_id: str, role: str):
        query = """
        MATCH (p:Person {id: $person_id})
        MATCH (c:Crime {id: $crime_id})
        MERGE (p)-[r:PARTICIPATED_IN]->(c)
        SET r.role = $role
        """
        await cls.run_query(query, {"person_id": person_id, "crime_id": crime_id, "role": role})

    @classmethod
    async def create_knows_relationship(cls, person_a: str, person_b: str, relationship_type: str = "associate"):
        query = """
        MATCH (a:Person {id: $person_a})
        MATCH (b:Person {id: $person_b})
        MERGE (a)-[r:KNOWS]-(b)
        SET r.relationship_type = $relationship_type,
            r.since = timestamp()
        """
        await cls.run_query(query, {
            "person_a": person_a,
            "person_b": person_b,
            "relationship_type": relationship_type,
        })

    @classmethod
    async def get_person_network(cls, person_id: str, depth: int = 2) -> dict:
        query = """
        MATCH path = (p:Person {id: $person_id})-[:KNOWS|PARTICIPATED_IN|MEMBER_OF*1..$depth]-(connected)
        RETURN path
        """
        results = await cls.run_query(query, {"person_id": person_id, "depth": depth})
        return results

    @classmethod
    async def find_shortest_path(cls, person_a: str, person_b: str, max_depth: int = 6):
        query = """
        MATCH path = shortestPath(
            (p1:Person {id: $person_a})-[:KNOWS|PARTICIPATED_IN|MEMBER_OF*..$max_depth]-(p2:Person {id: $person_b})
        )
        RETURN path
        """
        results = await cls.run_query(query, {
            "person_a": person_a,
            "person_b": person_b,
            "max_depth": max_depth,
        })
        return results

    @classmethod
    async def detect_suspicious_transactions(cls, min_amount: float = 100000, min_chain_length: int = 3):
        query = """
        MATCH path = (from:BankAccount)-[:TRANSFERRED_TO*$min_chain_length..6]->(to:BankAccount)
        WHERE ALL(r in relationships(path) WHERE r.amount >= $min_amount)
        RETURN path, length(path) as chain_length
        ORDER BY chain_length DESC
        LIMIT 20
        """
        results = await cls.run_query(query, {
            "min_amount": min_amount,
            "min_chain_length": min_chain_length,
        })
        return results

    @classmethod
    async def detect_circular_transactions(cls, min_cycle_length: int = 3, max_cycle_length: int = 8):
        query = """
        MATCH path = (start:BankAccount)-[:TRANSFERRED_TO*$min_cycle_length..$max_cycle_length]->(start)
        WITH path, relationships(path) as rels
        WHERE ALL(r in rels WHERE r.is_suspicious = true OR r.amount > 50000)
        RETURN [node in nodes(path) | node.account_number] as account_cycle,
               [r in rels | r.amount] as amounts,
               length(path) as cycle_length,
               reduce(s = 0, r in rels | s + r.amount) as total_cycled_amount
        ORDER BY total_cycled_amount DESC
        LIMIT 20
        """
        results = await cls.run_query(query, {
            "min_cycle_length": min_cycle_length,
            "max_cycle_length": max_cycle_length,
        })
        return results

    @classmethod
    async def detect_money_trails(cls, person_id: str, max_depth: int = 5):
        query = """
        MATCH (p:Person {id: $person_id})-[:HAS_ACCOUNT]->(acc:BankAccount)
        MATCH trail = (acc)-[:TRANSFERRED_TO*1..$max_depth]->(dest:BankAccount)
        WHERE NOT (dest)<-[:HAS_ACCOUNT]-(p)
        RETURN [node in nodes(trail) | node.account_number] as path,
               [r in relationships(trail) | r.amount] as amounts,
               [r in relationships(trail) | r.date] as dates,
               length(trail) as hop_count,
               reduce(s = 0, r in relationships(trail) | s + r.amount) as total_amount
        ORDER BY total_amount DESC
        LIMIT 10
        """
        results = await cls.run_query(query, {
            "person_id": person_id,
            "max_depth": max_depth,
        })
        return results
