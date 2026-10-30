# expect: fail
# Correct KMP, but resets to 0 after a match, so overlapping occurrences are lost.
def solve(text, pattern):
    m = len(pattern)
    lps = [0] * m
    length = 0
    for i in range(1, m):
        while length > 0 and pattern[i] != pattern[length]:
            length = lps[length - 1]
        if pattern[i] == pattern[length]:
            length += 1
        lps[i] = length
    starts = []
    matched = 0
    for i in range(len(text)):
        while matched > 0 and text[i] != pattern[matched]:
            matched = lps[matched - 1]
        if text[i] == pattern[matched]:
            matched += 1
        if matched == m:
            starts.append(i - m + 1)
            matched = 0
    return starts
