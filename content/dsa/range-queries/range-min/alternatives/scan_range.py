# expect: bronze
# Keep the list and scan the range on every query: O(n) per query.
class MinTree:
    def __init__(self, values):
        self.values = values

    def update(self, i, value):
        self.values[i] = value

    def query(self, l, r):
        return min(self.values[l : r + 1])
