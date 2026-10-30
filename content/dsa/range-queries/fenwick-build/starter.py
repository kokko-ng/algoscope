class Fenwick:
    def __init__(self, n):
        self.n = n
        self.tree = [0] * (n + 1)

    def update(self, i, delta):
        # add delta to the value at index i
        pass

    def prefix(self, i):
        # the sum of the first i values (indices 0 .. i - 1)
        return 0

    def range_sum(self, l, r):
        # the sum of indices l .. r, both included
        return 0
