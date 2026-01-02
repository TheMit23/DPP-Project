import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from anonymization.degree_anonymization import K_anonymize
from construction.priority_construction import priority_construction
from probing.probing import probe_graph
from data.generate_graphs import generate_graph, save_graph
from evaluation.check_feasible_graph import is_feasible
from evaluation.check_k_anonymous import is_k_degree_anonymous

def main():
    print("Hello, enter the graph style:")
    print("1. Random (Erdos-Renyi)")
    print("2. Scale-free (Barabasi-Albert)")
    
    # Get graph type
    graph_choice = input("Enter your choice (1 or 2): ").strip()
    
    # Validate choice
    if graph_choice not in ["1", "2"]:
        print("Invalid choice. Please enter 1 or 2.")
        return
    
    # Get common parameters
    n = int(input("Enter number of nodes: "))
    seed = int(input("Enter random seed (default 42): ") or "42")
    K = int(input("Enter k value for anonymization (default 3): ") or "3")
    
    # Get type-specific parameters and generate graph
    graph_kwargs = {}
    
    if graph_choice == "1":
        graph_type = "er"
        p = float(input("Enter edge probability p (0.0-1.0): "))
        graph_kwargs["p"] = p
    else:  # graph_choice == "2"
        graph_type = "ba"
        m = int(input("Enter edges per new node m (must be < n): "))
        graph_kwargs["m"] = m
    
    # Generate graph
    G = generate_graph(graph_type=graph_type, n=n, seed=seed, **graph_kwargs)
    deg = dict(G.degree())
    order = sorted(G.nodes(), key=lambda v: (-deg[v], str(v)))
    d = [deg[v] for v in order]
    #anonymize graph
    db = K_anonymize(d, K)
    db_map = {order[i]: db[i] for i in range(len(order))}
    #check if the graph is feasible
    while not is_feasible(db):
        print("Probing graph1...")
        d=probe_graph(d)
        db = K_anonymize(d, K)
        
    #construct graph
    G_anon = priority_construction(db_map, G)
    #probe graph
    while (G_anon) is None:
        print("Probing graph2...")
        d = probe_graph(d)
        db = K_anonymize(d, K)
        db_map = {order[i]: db[i] for i in range(len(order))}
        G_anon = priority_construction(db_map, G)
    
    # Save anonymized graph
    # Generate name for anonymized graph based on original graph parameters
    if is_k_degree_anonymous(G_anon, K):
        print("Anoninous")
    else:
        print("Not Anoninous")
    if graph_type == "er":
        anon_name = f"ER_n{n}_p{graph_kwargs['p']}_seed{seed}_anon_k{K}"
    else:  # graph_type == "ba"
        anon_name = f"BA_n{n}_m{graph_kwargs['m']}_seed{seed}_anon_k{K}"
    
    out_dir = Path("results/generated")
    save_graph(G_anon, out_dir, anon_name)
    print(f"Saved anonymized graph: {anon_name} -> {out_dir}")


if __name__ == "__main__":
    main()
    