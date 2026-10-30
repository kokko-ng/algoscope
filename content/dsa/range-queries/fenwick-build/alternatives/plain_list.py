# expect: bronze
# Store the values directly and add them up on every query: O(n) per sum, O(n^2) overall.
class Fenwick:
    def __init__(self, n):
        self.values = [0] * n

    def update(self, i, delta):
        self.values[i] += delta

    def prefix(self, i):
        total = 0
        for k in range(i):
            total += self.values[k]
        return total

    def range_sum(self, l, r):
        total = 0
        for k in range(l, r + 1):
            total += self.values[k]
        return total
