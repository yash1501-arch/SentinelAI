"""Synthetic criminal network data generator."""
import numpy as np
import pandas as pd
import networkx as nx


def generate_criminal_network(
    n_persons: int = 100,
    n_gangs: int = 5,
    seed: int = 42,
) -> nx.Graph:
    np.random.seed(seed)
    G = nx.Graph()

    gang_sizes = np.random.multinomial(
        n_persons - n_gangs,
        np.ones(n_gangs) / n_gangs,
    )

    for g in range(n_gangs):
        gang_name = f"GANG-{g:03d}"
        G.add_node(gang_name, type="gang", label=f"Gang {chr(65+g)}", metadata={"size": int(gang_sizes[g])})

        for _ in range(gang_sizes[g]):
            person_id = f"P-{np.random.randint(10000, 99999)}"
            role = np.random.choice(["leader", "enforcer", "recruiter", "foot soldier", "financier", "informant"],
                                     p=[0.05, 0.1, 0.1, 0.5, 0.1, 0.15])
            G.add_node(person_id, type="person", label=f"Person {person_id[2:]}",
                       metadata={"role": role, "gang": gang_name})

            G.add_edge(person_id, gang_name, relationship="member_of", weight=1.0)

            other_members = [n for n in G.nodes if n.startswith("P-") and n != person_id and any(
                G.has_edge(gang_name, n2) for n2 in G.neighbors(person_id) if n2.startswith("GANG-")
            )]
            n_connections = np.random.poisson(2)
            for _ in range(min(n_connections, len(other_members))):
                target = np.random.choice(other_members)
                rel = np.random.choice(["known", "co-conspirator", "family", "associate"])
                G.add_edge(person_id, target, relationship=rel, weight=np.random.uniform(0.3, 1.0))

    return G


def network_to_dataframes(G: nx.Graph) -> tuple:
    nodes = []
    for nid, attrs in G.nodes(data=True):
        nodes.append({
            "id": nid,
            "type": attrs.get("type", "unknown"),
            "label": attrs.get("label", nid),
            "metadata": str(attrs.get("metadata", {})),
        })

    edges = []
    for s, t, attrs in G.edges(data=True):
        edges.append({
            "source": s,
            "target": t,
            "relationship": attrs.get("relationship", "connected"),
            "weight": attrs.get("weight", 1.0),
        })

    return pd.DataFrame(nodes), pd.DataFrame(edges)
