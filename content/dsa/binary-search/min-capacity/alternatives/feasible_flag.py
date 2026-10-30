# expect: pass
# Searches from 1 with a feasibility check that rejects any package heavier than the capacity.
def solve(weights, days):
    def fits(capacity):
        used, load = 1, 0
        for w in weights:
            if w > capacity:
                return False
            if load + w > capacity:
                used += 1
                load = 0
            load += w
        return used <= days

    lo, hi = 1, sum(weights)
    answer = hi
    while lo <= hi:
        mid = (lo + hi) // 2
        if fits(mid):
            answer = mid
            hi = mid - 1
        else:
            lo = mid + 1
    return answer
