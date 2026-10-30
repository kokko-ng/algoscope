# expect: fail
# union links the items themselves instead of their roots, cutting a from its old group.
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.groups = n

    def find(self, x):
        while self.parent[x] != x:
            x = self.parent[x]
        return x

    def union(self, a, b):
        if self.find(a) == self.find(b):
            return False
        self.parent[a] = b
        self.groups -= 1
        return True

    def connected(self, a, b):
        return self.find(a) == self.find(b)

    def count(self):
        return self.groups
