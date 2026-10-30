# expect: pass
# Runs KMP once per distinct pattern and marks hits: O(p * (n + m)).
def solve(text, patterns):
    hit = [False] * len(text)
    for pattern in {tuple(p) for p in patterns}:
        m = len(pattern)
        lps = [0] * m
        length = 0
        for i in range(1, m):
            while length > 0 and pattern[i] != pattern[length]:
                length = lps[length - 1]
            if pattern[i] == pattern[length]:
                length += 1
            lps[i] = length
        matched = 0
        for i, ch in enumerate(text):
            while matched > 0 and ch != pattern[matched]:
                matched = lps[matched - 1]
            if ch == pattern[matched]:
                matched += 1
            if matched == m:
                hit[i - m + 1] = True
                matched = lps[m - 1]
    return [i for i, found in enumerate(hit) if found]
