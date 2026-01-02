from collections import Counter
import networkx as nx

def is_k_degree_anonymous(G: nx.Graph, k: int) -> bool:
    degrees = [d for _, d in G.degree()]
    counts = Counter(degrees)
    return all(c >= k for c in counts.values())

def degree_counts(G: nx.Graph):
    degrees = [d for _, d in G.degree()]
    return Counter(degrees)