from typing import List

def K_anonymize(d :List[int], k: int) -> List[int]:
    n = len(d)
    if n == 0 or k <= 1:
        # Return target degrees equal to original degrees
        return d
    db = d.copy()
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

        # if exactly k nodes left -> start a new group
        if n - i == k:
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
