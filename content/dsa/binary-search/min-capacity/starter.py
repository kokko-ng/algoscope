def solve(weights, days):
    # Packages ship in order. Each day carries a run of consecutive packages
    # whose total weight is at most the capacity.
    # Return the smallest capacity that ships everything within `days` days.
    return max(weights)
