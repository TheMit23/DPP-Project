import pickle
import networkx as nx

from anonymization.degree_anonymization import (
    get_sorted_degree_sequence,
    is_sorted_nonincreasing,
    is_k_anonymous_degree_sequence,
    is_only_raises,
    l1_cost,
    failing_degrees,
)
from anonymization.degree_anonymization import K_anonymize  # הפונקציה שלך

GRAPH_PATH = "results/generated/BA_n1000_m3_seed42.gpickle"
K = 10

def main():
    with open(GRAPH_PATH, "rb") as f:
        G: nx.Graph = pickle.load(f)

    d = get_sorted_degree_sequence(G)

    # sanity on input
    assert len(d) == G.number_of_nodes(), "Degree sequence length != number of nodes"
    assert is_sorted_nonincreasing(d), "Input degree sequence is not sorted non-increasing"

    db = K_anonymize(G, K)

    # invariants on output
    assert len(db) == len(d), "Output length changed"
    assert is_sorted_nonincreasing(db), "Output is not sorted non-increasing"
    assert is_only_raises(d, db), "Output decreased some degrees (should only add edges)"
    assert is_k_anonymous_degree_sequence(db, K), "Output is NOT k-anonymous"

    print("✅ All checks passed.")
    print("n =", len(d), "k =", K)
    print("L1 cost =", l1_cost(d, db))
    print("Top 15 d :", d[:15])
    print("Top 15 db:", db[:15])

    bad = failing_degrees(db, K)
    if bad:
        print("Violations (should be empty):", bad[:10])

if __name__ == "__main__":
    main()
