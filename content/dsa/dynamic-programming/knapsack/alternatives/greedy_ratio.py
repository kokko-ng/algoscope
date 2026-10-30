# expect: fail
# Greedy: pack items by best value per unit of weight while they fit.
def solve(weights, values, capacity):
    order = sorted(range(len(weights)), key=lambda i: values[i] / weights[i], reverse=True)
    room = capacity
    total = 0
    for i in order:
        if weights[i] <= room:
            room -= weights[i]
            total += values[i]
    return total
