# expect: slow
# From every start, extend with a set until a letter repeats.
def solve(letters):
    best = 0
    for i in range(len(letters)):
        seen = set()
        for j in range(i, len(letters)):
            if letters[j] in seen:
                break
            seen.add(letters[j])
        best = max(best, len(seen))
    return best
