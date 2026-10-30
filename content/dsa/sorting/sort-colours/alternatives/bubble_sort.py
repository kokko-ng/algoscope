# expect: slow
# Bubble sort in place: correct, but O(n^2).
def solve(colours):
    n = len(colours)
    for end in range(n - 1, 0, -1):
        for i in range(end):
            if colours[i] > colours[i + 1]:
                colours[i], colours[i + 1] = colours[i + 1], colours[i]
