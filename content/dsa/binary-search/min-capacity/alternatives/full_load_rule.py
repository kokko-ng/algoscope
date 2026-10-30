# expect: fail
# Wrong tie rule: starts a new day when the load would equal the capacity, though that load fits.
def solve(weights, days):
    def trips_needed(capacity):
        trips, load = 1, 0
        for w in weights:
            if load + w >= capacity:
                trips += 1
                load = 0
            load += w
        return trips

    lo, hi = max(weights), sum(weights)
    while lo < hi:
        mid = (lo + hi) // 2
        if trips_needed(mid) <= days:
            hi = mid
        else:
            lo = mid + 1
    return lo
