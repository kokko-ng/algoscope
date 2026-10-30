# expect: pass
# Two passes: count each colour, then overwrite colours in place. Still O(n).
def solve(colours):
    counts = [0, 0, 0]
    for c in colours:
        counts[c] += 1
    i = 0
    for c in range(3):
        for _ in range(counts[c]):
            colours[i] = c
            i += 1
