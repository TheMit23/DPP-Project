from typing import List
def is_feasible(db: List[int]) -> bool:
    if sum(db) % 2 != 0:
        return False
    left = [0]*len(db)
    for i in range(len(db)-1):
        if i==0:
            left[i]=db[i]
        else:
            left[i]=db[i]+left[i-1]
        rest_sum=0
        for j in range(i+1,len(db)):
            rest_sum+=min(db[j],i+1)
        if left[i]>i*(i+1)+rest_sum:
            return False
    return True