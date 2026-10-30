# expect: fail
# update writes the leaf but never recomputes the parents above it.
class MinTree:
    def __init__(self, values):
        self.n = len(values)
        self.tree = [0] * self.n + values
        for i in range(self.n - 1, 0, -1):
            self.tree[i] = min(self.tree[2 * i], self.tree[2 * i + 1])

    def update(self, i, value):
        self.tree[i + self.n] = value

    def query(self, l, r):
        best = self.tree[l + self.n]
        l += self.n
        r += self.n + 1
        while l < r:
            if l & 1:
                best = min(best, self.tree[l])
                l += 1
            if r & 1:
                r -= 1
                best = min(best, self.tree[r])
            l //= 2
            r //= 2
        return best
