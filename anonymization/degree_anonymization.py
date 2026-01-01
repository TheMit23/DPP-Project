import networkx as nx
from collections import Counter
from typing import List, Tuple
def get_sorted_degree_sequence(G: nx.Graph) -> List[int]:
    degrees = [deg for _, deg in G.degree()]
    degrees.sort(reverse=True)
    return degrees

def K_anonymize(G: nx.Graph, k: int) -> List[int]:
    d = get_sorted_degree_sequence(G)  # original degrees (sorted)
    n = len(d)
    if n == 0 or k <= 1:
        return d.copy()

    db = d.copy()

    # start first group of size k (or all if n < k)
    group_target = db[0]
    end = min(k, n)
    for t in range(0, end):
        db[t] = group_target

    i = end
    while i < n:
        # if not enough nodes left to start a new k-group -> must merge all remaining
        if n - i < k:
            for t in range(i, n):
                db[t] = group_target
            break
        if n-i==k:
            for t in range(i, n):
                db[t] = d[i]
            break

        # Cmerge = (group_target - d[i]) + I(d[i+1 .. i+k])
        Cmerge = (group_target - d[i]) + sum(d[i+1] - d[j] for j in range(i+1, i+k+1))

        # Cnew = I(d[i .. i+k-1])
        Cnew = sum(d[i] - d[j] for j in range(i, i+k))

        if Cmerge <= Cnew:
            # merge i into current group
            db[i] = group_target
            i += 1
        else:
            # start new group at i
            group_target = d[i]
            for t in range(i, i+k):
                db[t] = group_target
            i += k

    return db




def is_sorted_nonincreasing(arr: List[int]) -> bool:
    return all(arr[i] >= arr[i+1] for i in range(len(arr)-1))

def is_k_anonymous_degree_sequence(d: List[int], k: int) -> bool:
    counts = Counter(d)
    return all(cnt >= k for cnt in counts.values())

def is_only_raises(original: List[int], anonymized: List[int]) -> bool:
    # assumes same length
    return all(anonymized[i] >= original[i] for i in range(len(original)))

def l1_cost(original: List[int], anonymized: List[int]) -> int:
    return sum(abs(anonymized[i] - original[i]) for i in range(len(original)))

def failing_degrees(d: List[int], k: int) -> List[Tuple[int, int]]:
    """Return list of (degree, count) that violate k-anonymity."""
    c = Counter(d)
    return sorted([(deg, cnt) for deg, cnt in c.items() if cnt < k], key=lambda x: x[1])