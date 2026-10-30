# expect: fail
# Keys on the set of letters, ignoring how often each appears, so "aab" and "abb" share a group.
def solve(words):
    groups = {}
    for word in words:
        key = frozenset(word)
        if key not in groups:
            groups[key] = []
        groups[key].append(word)
    return list(groups.values())
