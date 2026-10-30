# expect: slow
# Try every capacity from the heaviest package upwards: correct, but thousands of passes.
def solve(weights, days):
    capacity = max(weights)
    while True:
        trips, load = 1, 0
        for w in weights:
            if load + w > capacity:
                trips += 1
                load = 0
            load += w
        if trips <= days:
            return capacity
        capacity += 1
