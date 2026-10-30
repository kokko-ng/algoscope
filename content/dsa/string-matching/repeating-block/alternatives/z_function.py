# expect: pass
# Z-function: the smallest p dividing n whose suffix matches the prefix all the way to the end.
def solve(text):
    n = len(text)
    z = [0] * n
    left = right = 0
    for i in range(1, n):
        if i < right:
            z[i] = min(right - i, z[i - left])
        while i + z[i] < n and text[z[i]] == text[i + z[i]]:
            z[i] += 1
        if i + z[i] > right:
            left, right = i, i + z[i]
    for p in range(1, n):
        if n % p == 0 and z[p] == n - p:
            return p
    return n
