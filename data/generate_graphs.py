from __future__ import annotations
import pickle
import argparse
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


def save_graph(G: nx.Graph, out_dir: Path, name: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    g_path = out_dir / f"{name}.gpickle"
    s_path = out_dir / f"{name}.json"

    with open(g_path, "wb") as f:
        pickle.dump(G, f)
    with s_path.open("w", encoding="utf-8") as f:
        json.dump(graph_stats(G), f, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic graphs for k-degree anonymization project.")
    parser.add_argument("--out", type=str, default="results/generated", help="Output directory")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--n", type=int, default=1000, help="Number of nodes")

    sub = parser.add_subparsers(dest="model", required=True)

    er = sub.add_parser("er", help="Erdos-Renyi G(n,p)")
    er.add_argument("--p", type=float, required=True, help="Edge probability")

    ba = sub.add_parser("ba", help="Barabasi-Albert scale-free")
    ba.add_argument("--m", type=int, required=True, help="Edges per new node")

    args = parser.parse_args()
    out_dir = Path(args.out)

    if args.model == "er":
        G = generate_er(n=args.n, p=args.p, seed=args.seed)
        name = f"ER_n{args.n}_p{args.p}_seed{args.seed}"
    else:
        G = generate_ba(n=args.n, m=args.m, seed=args.seed)
        name = f"BA_n{args.n}_m{args.m}_seed{args.seed}"

    save_graph(G, out_dir, name)
    print(f"Saved: {name} -> {out_dir}")


if __name__ == "__main__":
    main()
