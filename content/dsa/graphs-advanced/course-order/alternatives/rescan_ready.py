# expect: slow
# Repeatedly scan every course for one with nothing left to wait for: O(V^2).
def solve(n, prerequisites):
    unlocks = [[] for _ in range(n)]
    waiting = [0] * n
    for course, required in prerequisites:
        unlocks[required].append(course)
        waiting[course] += 1
    taken = [False] * n
    for _ in range(n):
        pick = -1
        for c in range(n):
            if not taken[c] and waiting[c] == 0:
                pick = c
                break
        if pick < 0:
            return False
        taken[pick] = True
        for nxt in unlocks[pick]:
            waiting[nxt] -= 1
    return True
