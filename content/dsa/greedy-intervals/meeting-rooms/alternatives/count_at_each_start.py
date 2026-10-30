# expect: slow
# For each meeting, count the meetings running at its start time: O(n^2).
def solve(meetings):
    most = 0
    for s, _ in meetings:
        busy = 0
        for start, end in meetings:
            if start <= s < end:
                busy += 1
        most = max(most, busy)
    return most
