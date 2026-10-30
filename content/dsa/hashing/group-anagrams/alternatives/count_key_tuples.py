# expect: pass
# Literal reading: a letter-count key, and groups returned as tuples in any order.
def solve(words):
    groups = {}
    for word in words:
        counts = [0] * 26
        for ch in word:
            counts[ord(ch) - ord("a")] += 1
        groups.setdefault(tuple(counts), []).append(word)
    return [tuple(g) for g in groups.values()]
