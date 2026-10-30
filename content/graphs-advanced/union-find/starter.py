class UnionFind:
    def __init__(self, n):
        # items are 0 .. n-1, each starting in its own group
        self.parent = list(range(n))

    def find(self, x):
        # return the root of x's group, compressing the path on the way
        pass

    def union(self, a, b):
        # merge the groups of a and b; return True if they were separate
        pass

    def connected(self, a, b):
        pass

    def count(self):
        # number of separate groups
        pass
