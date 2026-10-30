# expect: fail
# Treats any course seen before as a cycle, so two routes to the same requirement look like a loop.
def solve(n, prerequisites):
    needs = [[] for _ in range(n)]
    for course, required in prerequisites:
        needs[course].append(required)
    seen = [False] * n

    def cyclic(c):
        if seen[c]:
            return True
        seen[c] = True
        for r in needs[c]:
            if cyclic(r):
                return True
        return False

    for c in range(n):
        if not seen[c] and cyclic(c):
            return False
    return True
