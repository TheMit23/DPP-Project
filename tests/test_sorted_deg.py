import pickle
from anonymization.degree_anonymization import get_sorted_degree_sequence

with open("results/generated/ER_n1000_p0.01_seed42.gpickle", "rb") as f:
    G = pickle.load(f)
d_sorted = get_sorted_degree_sequence(G)

print("Number of nodes:", len(d_sorted))
print("Sorted (first 10):", d_sorted[:10])
print("Sorted (last 10):", d_sorted[-10:])
