# expect: pass
# Z-function over pattern + separator + text: z[i] is the longest common prefix of the whole string and its suffix at i.
def solve(text, pattern):
    m = len(pattern)
    s = pattern + [None] + text
    z = [0] * len(s)
    left = right = 0
    for i in range(1, len(s)):
        if i < right:
            z[i] = min(right - i, z[i - left])
        while i + z[i] < len(s) and s[z[i]] == s[i + z[i]]:
            z[i] += 1
        if i + z[i] > right:
            left, right = i, i + z[i]
    return [i - m - 1 for i in range(m + 1, len(s)) if z[i] >= m]
