# expect: pass
# Depth-first search looking for a back edge, with white, grey and black states.
def solve(n, prerequisites):
    needs = [[] for _ in range(n)]
    for course, required in prerequisites:
        needs[course].append(required)
    state = [0] * n

    def cyclic(c):
        state[c] = 1
        for r in needs[c]:
            if state[r] == 1 or (state[r] == 0 and cyclic(r)):
                return True
        state[c] = 2
        return False

    for c in range(n):
        if state[c] == 0 and cyclic(c):
            return False
    return True
