def solve(n, pairs):
    parent = list(range(n))
    size = [1] * n
    groups = n
    counts = []

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, b in pairs:
        ra, rb = find(a), find(b)
        if ra != rb:
            if size[ra] < size[rb]:
                ra, rb = rb, ra
            parent[rb] = ra
            size[ra] += size[rb]
            groups -= 1
        counts.append(groups)
    return counts
