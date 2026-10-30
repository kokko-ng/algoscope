# expect: pass
# A dict counting every prefix of every word, the empty one included, instead of a trie.
def solve(words, prefixes):
    seen = {}
    for w in words:
        for i in range(len(w) + 1):
            p = w[:i]
            seen[p] = seen.get(p, 0) + 1
    return [seen.get(p, 0) for p in prefixes]
