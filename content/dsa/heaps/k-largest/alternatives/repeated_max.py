# expect: slow
# Take the maximum and remove it, k times: O(nk).
def solve(nums, k):
    rest = list(nums)
    out = []
    for _ in range(k):
        best = 0
        for i in range(1, len(rest)):
            if rest[i] > rest[best]:
                best = i
        rest[best], rest[-1] = rest[-1], rest[best]
        out.append(rest.pop())
    return out
