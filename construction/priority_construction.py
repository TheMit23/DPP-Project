from typing import Dict, Any, Optional
import networkx as nx


def priority_construction(db_map: Dict[Any, int], G: nx.Graph) -> Optional[nx.Graph]:
    """
    Returns:
        nx.Graph if successful, otherwise None.
    """

    # --- Basic sanity checks ---
    for v in G.nodes():
        if v not in db_map:
            raise ValueError(f"db_map missing node {v}")
        if db_map[v] < 0:
            return None
        if db_map[v] > len(G.nodes()) - 1:
            return None

    # Start from empty graph with same node set
    G_anon = nx.Graph()
    G_anon.add_nodes_from(G.nodes())

    # need[v] = how many more incident edges v still needs in G_anon
    need = {v: int(db_map[v]) for v in G.nodes()}

    # Helper for candidate legality
    def can_add_edge(v, u) -> bool:
        if v == u:
            return False
        if need[v] <= 0 or need[u] <= 0:
            return False
        if G_anon.has_edge(v, u):
            return False
        return True

    # Strategy for picking next vertex to satisfy (most constrained / highest need)
    def pick_vertex():
        return max((v for v in G_anon.nodes() if need[v] > 0), key=lambda x: need[x])

    # Main loop
    while True:
        active = [v for v in G_anon.nodes() if need[v] > 0]
        if not active:
            break  # success
        v = pick_vertex()
        # Try to connect v to its original neighbors first
        for u in G.neighbors(v):
            if need[v] == 0:
                break
            if can_add_edge(v, u):
                G_anon.add_edge(v, u)
                need[v] -= 1
                need[u] -= 1
        #adds new edges
        if need[v] > 0:
            candidates = [
                u for u in G_anon.nodes()
                if can_add_edge(v, u) and not G.has_edge(v, u)  # ensure it's a "new" edge
            ]
            # Prefer high-need endpoints (ConstructGraph style)
            candidates.sort(key=lambda x: need[x], reverse=True)

            for u in candidates:
                if need[v] == 0:
                    break
                if can_add_edge(v, u):  
                    G_anon.add_edge(v, u)
                    need[v] -= 1
                    need[u] -= 1

        # Failure: still cannot satisfy v
        if need[v] > 0:
            return None

    # Final verification: degrees match targets
    for v in G_anon.nodes():
        if G_anon.degree(v) != db_map[v]:
            return None

    return G_anon

