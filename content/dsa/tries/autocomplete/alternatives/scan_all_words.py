# expect: slow
# For every query, scan the whole word list, then sort the matches: O(n^2).
def solve(words, queries):
    unique = sorted(set(words))
    out = []
    for q in queries:
        found = []
        for w in unique:
            if w[: len(q)] == q:
                found.append(w)
                if len(found) == 3:
                    break
        out.append(found)
    return out
