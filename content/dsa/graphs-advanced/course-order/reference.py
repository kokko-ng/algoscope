from collections import deque


def solve(n, prerequisites):
    unlocks = {course: [] for course in range(n)}
    waiting = [0] * n
    for course, required in prerequisites:
        unlocks[required].append(course)
        waiting[course] += 1
    ready = deque(course for course in range(n) if waiting[course] == 0)
    taken = []
    while ready:
        course = ready.popleft()
        taken.append(course)
        for nxt in unlocks[course]:
            waiting[nxt] -= 1
            if waiting[nxt] == 0:
                ready.append(nxt)
    return len(taken) == n
