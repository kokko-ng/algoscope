# expect: fail
# Returns n - lps[-1] without checking that it divides n: "abcab" gives 3 instead of 5.
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
    return n - lps[-1]
