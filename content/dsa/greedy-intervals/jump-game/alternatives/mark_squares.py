# expect: slow
# Mark every square each reachable position can jump to: O(n^2) with long jumps.
def solve(jumps):
    n = len(jumps)
    reachable = [False] * n
    reachable[0] = True
    for i in range(n):
        if not reachable[i]:
            continue
        for j in range(i + 1, min(n, i + jumps[i] + 1)):
            reachable[j] = True
    return reachable[n - 1]
