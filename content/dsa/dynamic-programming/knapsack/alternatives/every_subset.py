# expect: slow
# Plain recursion over every take-or-skip choice, without memo: 2^n.
def solve(weights, values, capacity):
    def best(i, room):
        if i == len(weights):
            return 0
        skip = best(i + 1, room)
        if weights[i] <= room:
            return max(skip, values[i] + best(i + 1, room - weights[i]))
        return skip

    return best(0, capacity)
