# expect: fail
# Restarts from the first pattern character on a mismatch instead of using the failure table.
def solve(text, pattern):
    m = len(pattern)
    starts = []
    matched = 0
    for i in range(len(text)):
        if text[i] == pattern[matched]:
            matched += 1
        else:
            matched = 1 if text[i] == pattern[0] else 0
        if matched == m:
            starts.append(i - m + 1)
            matched = 0
    return starts
