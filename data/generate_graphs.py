from __future__ import annotations
import pickle
import json
from pathlib import Path

import networkx as nx


def graph_stats(G: nx.Graph) -> dict:
    n = G.number_of_nodes()
    m = G.number_of_edges()

    # Connected components + safe APL
    if n == 0:
        apl = None
        largest_cc = []
    else:
        comps = list(nx.connected_components(G))
        largest_cc = max(comps, key=len) if comps else []
        if len(largest_cc) >= 2:
            H = G.subgraph(largest_cc).copy()
            apl = nx.average_shortest_path_length(H)
        else:
            apl = None

    cc = nx.average_clustering(G) if n >= 2 else 0.0
    degrees = [d for _, d in G.degree()]
    dmax = max(degrees) if degrees else 0
    dmin = min(degrees) if degrees else 0
    davg = (sum(degrees) / len(degrees)) if degrees else 0.0

    return {
        "nodes": n,
        "edges": m,
        "avg_clustering": cc,
        "avg_path_length_lcc": apl,  # APL on Largest Connected Component
        "degree_min": dmin,
        "degree_max": dmax,
        "degree_avg": davg,
        "connected_components": len(list(nx.connected_components(G))) if n else 0,
        "largest_component_size": len(largest_cc),
    }


def generate_er(n: int, p: float, seed: int) -> nx.Graph:
    return nx.erdos_renyi_graph(n=n, p=p, seed=seed)


def generate_ba(n: int, m: int, seed: int) -> nx.Graph:
    # Barabási–Albert requires 1 <= m < n
    if not (1 <= m < n):
        raise ValueError("BA requires 1 <= m < n")
    return nx.barabasi_albert_graph(n=n, m=m, seed=seed)


def generate_graph(graph_type: str, n: int, seed: int = 42, out_dir: str | Path = "results/generated", **kwargs) -> nx.Graph:
    """
    Returns:
        Generated NetworkX graph
    """
    # Generate the graph
    if graph_type == "er":
        if "p" not in kwargs:
            raise ValueError("Erdos-Renyi graph requires 'p' parameter (edge probability)")
        G = generate_er(n=n, p=kwargs["p"], seed=seed)
        name = f"ER_n{n}_p{kwargs['p']}_seed{seed}"
    elif graph_type == "ba":
        if "m" not in kwargs:
            raise ValueError("Barabasi-Albert graph requires 'm' parameter (edges per new node)")
        G = generate_ba(n=n, m=kwargs["m"], seed=seed)
        name = f"BA_n{n}_m{kwargs['m']}_seed{seed}"
    else:
        raise ValueError(f"Unknown graph type: {graph_type}. Supported types: 'er', 'ba'")
    
    # Save the graph and its stats
    out_dir_path = Path(out_dir)
    save_graph(G, out_dir_path, name)
    
    return G


def save_graph(G: nx.Graph, out_dir: Path, name: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    g_path = out_dir / f"{name}.gpickle"
    s_path = out_dir / f"{name}.json"

    with open(g_path, "wb") as f:
        pickle.dump(G, f)
    with s_path.open("w", encoding="utf-8") as f:
        json.dump(graph_stats(G), f, indent=2)
