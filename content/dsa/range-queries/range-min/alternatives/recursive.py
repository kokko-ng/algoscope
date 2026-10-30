# expect: pass
# A recursive segment tree: node k covers [lo, hi] and its children cover the two halves.
class MinTree:
    def __init__(self, values):
        self.n = len(values)
        self.tree = [0] * (4 * self.n)
        self._build(1, 0, self.n - 1, values)

    def _build(self, k, lo, hi, values):
        if lo == hi:
            self.tree[k] = values[lo]
            return
        mid = (lo + hi) // 2
        self._build(2 * k, lo, mid, values)
        self._build(2 * k + 1, mid + 1, hi, values)
        self.tree[k] = min(self.tree[2 * k], self.tree[2 * k + 1])

    def update(self, i, value, k=1, lo=0, hi=None):
        if hi is None:
            hi = self.n - 1
        if lo == hi:
            self.tree[k] = value
            return
        mid = (lo + hi) // 2
        if i <= mid:
            self.update(i, value, 2 * k, lo, mid)
        else:
            self.update(i, value, 2 * k + 1, mid + 1, hi)
        self.tree[k] = min(self.tree[2 * k], self.tree[2 * k + 1])

    def query(self, l, r, k=1, lo=0, hi=None):
        if hi is None:
            hi = self.n - 1
        if l <= lo and hi <= r:
            return self.tree[k]
        mid = (lo + hi) // 2
        if r <= mid:
            return self.query(l, r, 2 * k, lo, mid)
        if l > mid:
            return self.query(l, r, 2 * k + 1, mid + 1, hi)
        return min(self.query(l, r, 2 * k, lo, mid), self.query(l, r, 2 * k + 1, mid + 1, hi))
