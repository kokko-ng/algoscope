def solve(text):
    n = len(text)
    lps = [0] * n
    length = 0
    for i in range(1, n):
        while length > 0 and text[i] != text[length]:
            length = lps[length - 1]
        if text[i] == text[length]:
            length += 1
        lps[i] = length
    period = n - lps[-1]
    return period if n % period == 0 else n
