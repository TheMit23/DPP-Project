import pickle
import networkx as nx
from collections import Counter
from typing import Dict, Any, List, Tuple

from anonymization.degree_anonymization import K_anonymize  # now returns Dict[node, int]

GRAPH_PATH = "results/generated/BA_n1000_m3_seed42.gpickle"
K = 10


# ---------- helpers on MAP output ----------

def is_k_anonymous_map(db_map: Dict[Any, int], k: int) -> bool:
    c = Counter(db_map.values())
    return all(cnt >= k for cnt in c.values())

def failing_degrees_map(db_map: Dict[Any, int], k: int) -> List[Tuple[int, int]]:
    c = Counter(db_map.values())
    return sorted([(deg, cnt) for deg, cnt in c.items() if cnt < k], key=lambda x: x[1])

def is_only_raises_map(G: nx.Graph, db_map: Dict[Any, int]) -> bool:
    deg = dict(G.degree())
    return all(db_map[v] >= deg[v] for v in G.nodes())

def l1_cost_map(G: nx.Graph, db_map: Dict[Any, int]) -> int:
    deg = dict(G.degree())
    return sum(abs(db_map[v] - deg[v]) for v in G.nodes())

def is_nonincreasing_wrt_original_order(G: nx.Graph, db_map: Dict[Any, int]) -> bool:
    """
    Check that if you sort vertices by original degree descending,
    the assigned target degrees are non-increasing along that order.
    This matches the paper/your algorithm assumption (working on sorted degree sequence),
    WITHOUT sorting db_map by its values.
    """
    deg = dict(G.degree())
    order = sorted(G.nodes(), key=lambda v: (-deg[v], str(v)))
    return all(db_map[order[i]] >= db_map[order[i+1]] for i in range(len(order) - 1))

def sanity_values(db_map: Dict[Any, int], n: int) -> bool:
    return all(isinstance(x, int) and 0 <= x <= n-1 for x in db_map.values())


def main():
    with open(GRAPH_PATH, "rb") as f:
        G: nx.Graph = pickle.load(f)

    n = G.number_of_nodes()

    db_map = K_anonymize(G, K)  # Dict[node, int]

    # ----- tests directly on map output -----

    # 1) keys match nodes
    assert set(db_map.keys()) == set(G.nodes()), "db_map keys must match exactly G.nodes()"

    # 2) values are valid degrees
    assert sanity_values(db_map, n), "db_map has invalid degree values (not int / out of range)"

    # 3) only raises (since construction is add-edges only)
    assert is_only_raises_map(G, db_map), "Some nodes decreased degree (should only add edges)"

    # 4) k-anonymous on the multiset of target degrees
    assert is_k_anonymous_map(db_map, K), "Target degrees are NOT k-anonymous"

    # 5) non-increasing along original-degree ranking (algorithm works on sorted degree sequence)
    assert is_nonincreasing_wrt_original_order(G, db_map), (
        "Target degrees are not non-increasing when nodes are ordered by original degree"
    )

    # reporting
    print("✅ All MAP-output checks passed.")
    print("n =", n, "k =", K)
    print("L1 cost (node-wise) =", l1_cost_map(G, db_map))

    bad = failing_degrees_map(db_map, K)
    if bad:
        print("Violations (should be empty):", bad[:10])


if __name__ == "__main__":
    main()
