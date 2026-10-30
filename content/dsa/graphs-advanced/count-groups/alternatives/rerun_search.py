# expect: slow
# After every link, count the groups again with a fresh graph search: O(m·(n + m)).
def solve(n, pairs):
    adj = [[] for _ in range(n)]
    counts = []
    for a, b in pairs:
        adj[a].append(b)
        adj[b].append(a)
        seen = [False] * n
        groups = 0
        for s in range(n):
            if seen[s]:
                continue
            groups += 1
            seen[s] = True
            stack = [s]
            while stack:
                x = stack.pop()
                for y in adj[x]:
                    if not seen[y]:
                        seen[y] = True
                        stack.append(y)
        counts.append(groups)
    return counts
