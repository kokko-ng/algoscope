# expect: slow
# Test every prefix against every word: O(n^2).
def solve(words, prefixes):
    counts = []
    for p in prefixes:
        total = 0
        for w in words:
            if w[: len(p)] == p:
                total += 1
        counts.append(total)
    return counts
