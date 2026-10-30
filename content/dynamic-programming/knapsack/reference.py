def solve(weights, values, capacity):
    best = [[0] * (capacity + 1) for _ in range(len(weights) + 1)]
    for item in range(1, len(weights) + 1):
        weight, value = weights[item - 1], values[item - 1]
        for room in range(capacity + 1):
            best[item][room] = best[item - 1][room]
            if weight <= room:
                best[item][room] = max(best[item][room], best[item - 1][room - weight] + value)
    return best[len(weights)][capacity]
