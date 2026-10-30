# expect: pass
# The 0-based variant: slot i covers indices (i & (i + 1)) .. i.
class Fenwick:
    def __init__(self, n):
        self.n = n
        self.tree = [0] * n

    def update(self, i, delta):
        while i < self.n:
            self.tree[i] += delta
            i |= i + 1

    def prefix(self, i):
        total = 0
        i -= 1
        while i >= 0:
            total += self.tree[i]
            i = (i & (i + 1)) - 1
        return total

    def range_sum(self, l, r):
        return self.prefix(r + 1) - self.prefix(l)
