# expect: fail
# Collects matches without removing repeated words.
def solve(words, queries):
    out = []
    for q in queries:
        matches = [w for w in words if w[: len(q)] == q]
        matches.sort()
        out.append(matches[:3])
    return out
