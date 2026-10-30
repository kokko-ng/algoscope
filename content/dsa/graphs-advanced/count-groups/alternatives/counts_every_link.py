# expect: fail
# Lowers the count for every link, even one inside a group that is already joined.
def solve(n, pairs):
    parent = list(range(n))
    groups = n
    counts = []

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, b in pairs:
        parent[find(a)] = find(b)
        groups -= 1
        counts.append(groups)
    return counts
