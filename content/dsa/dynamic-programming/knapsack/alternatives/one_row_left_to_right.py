# expect: fail
# Fills the single row left to right, so an item can be packed again and again.
def solve(weights, values, capacity):
    best = [0] * (capacity + 1)
    for weight, value in zip(weights, values):
        for room in range(weight, capacity + 1):
            if best[room - weight] + value > best[room]:
                best[room] = best[room - weight] + value
    return best[capacity]
