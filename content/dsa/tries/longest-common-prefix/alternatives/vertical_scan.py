# expect: pass
# No trie: compare column by column across all words until one differs or ends.
def solve(words):
    if not words:
        return ""
    i = 0
    while True:
        for w in words:
            if i == len(w) or w[i] != words[0][i]:
                return words[0][:i]
        i += 1
