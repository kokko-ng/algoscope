# expect: bronze
# Try every start and compare character by character: O(n * m).
def solve(text, pattern):
    m = len(pattern)
    starts = []
    for i in range(len(text) - m + 1):
        k = 0
        while k < m and text[i + k] == pattern[k]:
            k += 1
        if k == m:
            starts.append(i)
    return starts
