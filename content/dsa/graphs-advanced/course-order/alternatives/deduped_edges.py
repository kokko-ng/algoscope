# expect: fail
# Stores unlocks in sets but counts every pair, so a repeated prerequisite is never cleared.
from collections import deque


def solve(n, prerequisites):
    unlocks = [set() for _ in range(n)]
    waiting = [0] * n
    for course, required in prerequisites:
        unlocks[required].add(course)
        waiting[course] += 1
    ready = deque(c for c in range(n) if waiting[c] == 0)
    taken = 0
    while ready:
        c = ready.popleft()
        taken += 1
        for nxt in unlocks[c]:
            waiting[nxt] -= 1
            if waiting[nxt] == 0:
                ready.append(nxt)
    return taken == n
