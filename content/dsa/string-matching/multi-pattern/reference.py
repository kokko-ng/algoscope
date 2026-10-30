def solve(text, patterns):
    m = len(patterns[0])
    base, mod = 131, 1_000_000_007
    targets = set()
    for pattern in patterns:
        code = 0
        for ch in pattern:
            code = (code * base + ord(ch)) % mod
        targets.add(code)
    high = pow(base, m - 1, mod)
    starts = []
    window = 0
    for i in range(len(text)):
        if i >= m:
            window = (window - ord(text[i - m]) * high) % mod
        window = (window * base + ord(text[i])) % mod
        start = i - m + 1
        if start >= 0 and window in targets and text[start : i + 1] in patterns:
            starts.append(start)
    return starts
