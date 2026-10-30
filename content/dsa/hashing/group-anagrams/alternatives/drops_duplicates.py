# expect: fail
# Stores each group as a set, so repeated words collapse into one.
def solve(words):
    groups = {}
    for word in words:
        groups.setdefault("".join(sorted(word)), set()).add(word)
    return [list(g) for g in groups.values()]
