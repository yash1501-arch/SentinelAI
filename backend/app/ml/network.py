import sys
import asyncio
from pathlib import Path

ML_SERVICES_DIR = Path(__file__).resolve().parents[2] / "ml-services"
sys.path.insert(0, str(ML_SERVICES_DIR))


async def compute_centrality(nodes: list, edges: list) -> dict:
    try:
        from network.model import compute_centrality as _cc
        graph_data = {
            "nodes": [{"id": n.id, "type": n.type, "label": n.label} for n in nodes],
            "edges": [{"source": e.source, "target": e.target, "relationship": e.relationship} for e in edges],
        }
        result = await asyncio.to_thread(_cc, graph_data)
        if result:
            return {
                label: vals["degree"]
                for n in nodes
                for vals in [result.get(n.id, {})]
                for label in [n.label]
            }
    except Exception:
        pass
    return {}


async def detect_communities_ml(nodes: list, edges: list) -> list:
    try:
        import networkx as nx
        G = nx.Graph()
        for n in nodes:
            G.add_node(n.id, label=n.label, type=n.type)
        for e in edges:
            G.add_edge(e.source, e.target, relationship=e.relationship)
        communities = list(nx.community.greedy_modularity_communities(G))
        return [
            [G.nodes[n].get("label", n) for n in comm]
            for comm in communities if len(comm) >= 2
        ]
    except Exception:
        return []
