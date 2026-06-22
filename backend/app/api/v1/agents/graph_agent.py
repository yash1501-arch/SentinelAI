import json
import time
from app.core.config import settings
from app.services.openai_client import create_openai_client
from app.llm.state import AgentState
from app.services.neo4j_service import Neo4jService

client = create_openai_client()

CYPHER_PROMPT = """
You are the Graph Agent for Sentinel AI. Convert natural language into Cypher queries for Neo4j.

Graph Schema:
Nodes: Person, Crime, Location, Vehicle, BankAccount, Phone, Organization, Gang, Weapon, Victim, Accused, Witness

Relationships:
- (p:Person)-[:PARTICIPATED_IN {role: "victim"|"accused"|"witness"}]->(c:Crime)
- (p1:Person)-[:KNOWS {relationship_type: string, since: date}]->(p2:Person)
- (p:Person)-[:OWNS]->(v:Vehicle)
- (p:Person)-[:HAS_ACCOUNT]->(a:BankAccount)
- (a1:BankAccount)-[:TRANSFERRED_TO {amount: float, date: datetime, is_suspicious: bool}]->(a2:BankAccount)
- (p:Person)-[:MEMBER_OF_GANG {role: string}]->(g:Gang)
- (p:Person)-[:MEMBER_OF]->(o:Organization)
- (c:Crime)-[:OCCURRED_AT]->(l:Location)
- (c:Crime)-[:SIMILAR_TO {score: float}]->(c2:Crime)
- (g1:Gang)-[:RIVAL_OF]->(g2:Gang)
- (p:Person)-[:FINANCIAL_LINK {total_amount: float}]->(p2:Person)

Common Query Patterns:
- Network: MATCH (p:Person {{id: $id}})-[:KNOWS|MEMBER_OF*1..{depth}]-(connected)
- Shortest path: MATCH path = shortestPath((p1)-[*..6]-(p2))
- Money trail: MATCH path = (a:BankAccount)-[:TRANSFERRED_TO*3..6]->(b)
- Community: CALL gds.louvain.stream('crime-graph')
- Centrality: CALL gds.pageRank.stream('crime-graph')
- Repeat offenders: MATCH (a:Accused)-[:PARTICIPATED_IN]->(c:Crime) WITH a, count(c) as cnt WHERE cnt > 1

User Query: {query}

Respond ONLY with a JSON object:
{{"cypher": "MATCH ... RETURN ...", "explanation": "purpose of query", "params": {{}}}}
"""


class GraphAgent:
    async def run(self, state: AgentState) -> AgentState:
        start = time.time()

        try:
            response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": CYPHER_PROMPT.format(query=state["query"])},
                ],
                temperature=0.0,
                max_tokens=500,
            )

            result = json.loads(response.choices[0].message.content.strip())
            cypher = result.get("cypher", "").strip()
            params = result.get("params", {})
            state["cypher_query"] = cypher
            state["reasoning_chain"].append(f"Graph Agent generated Cypher: {result.get('explanation', '')}")

            if cypher:
                state["graph_result"] = await Neo4jService.run_query(cypher, params)
                state["reasoning_chain"].append(
                    f"Graph Agent executed query, returned {len(state['graph_result'])} records"
                )
            else:
                state["graph_result"] = []
                state["graph_error"] = "Empty Cypher generated"

        except Exception as e:
            state["graph_error"] = str(e)
            state["graph_result"] = []
            state["reasoning_chain"].append(f"Graph Agent error: {str(e)}")

        state["processing_time_ms"] = int((time.time() - start) * 1000)
        return state
