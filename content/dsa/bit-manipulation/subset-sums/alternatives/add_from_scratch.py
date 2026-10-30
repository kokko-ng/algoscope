# expect: slow
# Tests all n bits of every mask: O(n * 2^n).
def solve(items):
    sums = []
    for mask in range(1 << len(items)):
        total = 0
        for i in range(len(items)):
            if mask >> i & 1:
                total += items[i]
        sums.append(total)
    return sums
