# expect: slow
# Compare each word's sorted letters with every existing group: correct, but O(n^2).
def solve(words):
    groups = []
    keys = []
    for word in words:
        key = sorted(word)
        for g in range(len(keys)):
            if keys[g] == key:
                groups[g].append(word)
                break
        else:
            keys.append(key)
            groups.append([word])
    return groups
