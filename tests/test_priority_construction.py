import pickle
import networkx as nx
from collections import Counter
from typing import Dict, Any, List, Tuple, Optional

from anonymization.degree_anonymization import K_anonymize
from construction.priority_construction import priority_construction 

GRAPH_PATH = "results/generated/BA_n1000_m3_seed42.gpickle"
K = 10


# ---------- helpers ----------

def is_k_anonymous_degrees(degs: List[int], k: int) -> bool:
    c = Counter(degs)
    return all(cnt >= k for cnt in c.values())

def failing_degrees(degs: List[int], k: int) -> List[Tuple[int, int]]:
    c = Counter(degs)
    return sorted([(deg, cnt) for deg, cnt in c.items() if cnt < k], key=lambda x: x[1])

def degree_multiset(G: nx.Graph) -> List[int]:
    return [deg for _, deg in G.degree()]

def edge_overlap_ratio(G_orig: nx.Graph, G_new: nx.Graph) -> float:
    """
    How many edges in G_new are also in G_orig (undirected).
    Useful to verify the "priority" effect (not a correctness invariant).
    """
    Eo = {tuple(sorted(e)) for e in G_orig.edges()}
    En = {tuple(sorted(e)) for e in G_new.edges()}
    if not En:
        return 0.0
    return len(Eo & En) / len(En)

def assert_degrees_match_db_map(G_anon: nx.Graph, db_map: Dict[Any, int]) -> None:
    for v, target in db_map.items():
        assert G_anon.degree(v) == target, f"Degree mismatch for {v}: got {G_anon.degree(v)}, expected {target}"

def assert_no_self_loops(G_anon: nx.Graph) -> None:
    loops = list(nx.selfloop_edges(G_anon))
    assert len(loops) == 0, f"Graph has self-loops: {loops[:5]}"

def assert_nodes_match(G_orig: nx.Graph, G_anon: nx.Graph) -> None:
    assert set(G_anon.nodes()) == set(G_orig.nodes()), "Node sets differ between original and anonymized graph"


def main():
    with open(GRAPH_PATH, "rb") as f:
        G: nx.Graph = pickle.load(f)

    n = G.number_of_nodes()

    # --- 1) produce target degrees (map output) ---
    db_map: Dict[Any, int] = K_anonymize(G, K)

    # sanity on db_map itself
    assert set(db_map.keys()) == set(G.nodes()), "db_map keys must match exactly G.nodes()"
    assert all(isinstance(x, int) for x in db_map.values()), "db_map values must be ints"
    assert all(0 <= db_map[v] <= n - 1 for v in G.nodes()), "db_map contains invalid degrees (out of range)"
    assert sum(db_map.values()) % 2 == 0, "Sum of target degrees must be even (necessary for realization)"
    assert is_k_anonymous_degrees(list(db_map.values()), K), "Target degrees are NOT k-anonymous"

    # --- 2) build graph using priority construction ---
    # IMPORTANT: do NOT allow priority_construction to mutate db_map in-place!
    G_anon: Optional[nx.Graph] = priority_construction(db_map.copy(), G)

    assert G_anon is not None, "priority_construction failed (returned None)"
    assert isinstance(G_anon, nx.Graph), "priority_construction must return an nx.Graph on success"

    # --- 3) correctness invariants on the constructed graph ---
    assert_nodes_match(G, G_anon)
    assert_no_self_loops(G_anon)

    # degrees must match targets exactly
    assert_degrees_match_db_map(G_anon, db_map)

    # k-anonymity should hold on realized degrees as well (same multiset)
    anon_degs = degree_multiset(G_anon)
    assert is_k_anonymous_degrees(anon_degs, K), "Constructed graph degrees are NOT k-anonymous (unexpected)"

    # --- 4) optional: check 'priority' behavior (not required, but informative) ---
    overlap = edge_overlap_ratio(G, G_anon)
    print("✅ Priority construction checks passed.")
    print("n =", n, "k =", K)
    print("m_orig =", G.number_of_edges(), "m_anon =", G_anon.number_of_edges())
    print("Edge overlap ratio (orig ∩ anon / anon) =", round(overlap, 4))

    bad = failing_degrees(anon_degs, K)
    if bad:
        print("Violations (should be empty):", bad[:10])


if __name__ == "__main__":
    main()
