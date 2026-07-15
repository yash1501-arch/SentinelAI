"""Network analysis: centrality, community detection, and suspicious pattern discovery."""
import os
import json
import networkx as nx

from .data import generate_criminal_network

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODELS_DIR, exist_ok=True)


def analyze(save: bool = True) -> dict:
    G = generate_criminal_network(100, 5)

    degree_cent = nx.degree_centrality(G)
    nx.betweenness_centrality(G)
    nx.eigenvector_centrality(G, max_iter=1000)

    persons = [n for n in G.nodes if G.nodes[n].get("type") == "person"]
    gangs = [n for n in G.nodes if G.nodes[n].get("type") == "gang"]

    top_degree = sorted(
        [(n, degree_cent[n], G.nodes[n].get("metadata", {}).get("role", ""))
         for n in persons if n in degree_cent],
        key=lambda x: x[1], reverse=True,
    )[:10]

    communities = list(nx.community.greedy_modularity_communities(G))
    modularity = nx.community.modularity(G, communities)

    suspicious_patterns = []
    for node in persons:
        neighbors = list(G.neighbors(node))
        for n1 in neighbors:
            for n2 in neighbors:
                if n1 != n2 and n1.startswith("P-") and n2.startswith("P-"):
                    if not G.has_edge(n1, n2) and n1 != n2:
                        suspicious_patterns.append({
                            "type": "missing_direct_link",
                            "person_a": node,
                            "person_b": n1,
                            "person_c": n2,
                        })

    triangles = []
    for triangle in nx.enumerate_all_cliques(G):
        if len(triangle) == 3:
            triangles.append(triangle)
    n_triangles = len(triangles)

    bridges = list(nx.bridges(G))
    n_bridges = len(bridges)

    metrics = {
        "n_nodes": G.number_of_nodes(),
        "n_edges": G.number_of_edges(),
        "n_gangs": len(gangs),
        "n_persons": len(persons),
        "density": round(nx.density(G), 4),
        "modularity": round(modularity, 4),
        "n_communities": len(communities),
        "n_triangles": n_triangles,
        "n_bridges": n_bridges,
        "n_suspicious_patterns": len(suspicious_patterns),
        "top_central_persons": [
            {"id": n, "centrality": round(c, 4), "role": r}
            for n, c, r in top_degree
        ],
        "suspicious_patterns_sampled": suspicious_patterns[:10],
    }

    if save:
        with open(os.path.join(MODELS_DIR, "graph_metrics.json"), "w") as f:
            json.dump(metrics, f, indent=2, default=str)
        nx.write_gexf(G, os.path.join(MODELS_DIR, "criminal_network.gexf"))
        print(f"Analysis saved to {MODELS_DIR}")

    return metrics


def compute_centrality(graph_data: dict) -> dict:
    G = nx.Graph()
    for node in graph_data.get("nodes", []):
        G.add_node(node["id"], type=node.get("type", "unknown"), label=node.get("label", ""))
    for edge in graph_data.get("edges", []):
        G.add_edge(edge["source"], edge["target"], relationship=edge.get("relationship", "connected"))

    if G.number_of_nodes() == 0:
        return {}

    cent = {
        "degree": nx.degree_centrality(G),
        "betweenness": nx.betweenness_centrality(G),
        "eigenvector": nx.eigenvector_centrality(G, max_iter=1000),
    }

    return {
        node_id: {
            "degree": round(cent["degree"].get(node_id, 0), 4),
            "betweenness": round(cent["betweenness"].get(node_id, 0), 4),
            "eigenvector": round(cent["eigenvector"].get(node_id, 0), 4),
        }
        for node_id in G.nodes
    }


if __name__ == "__main__":
    metrics = analyze()
    print(json.dumps(metrics, indent=2, default=str))
