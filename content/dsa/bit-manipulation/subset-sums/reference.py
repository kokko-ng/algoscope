def solve(items):
    sums = [0] * (1 << len(items))
    for mask in range(1, len(sums)):
        low = mask & -mask
        sums[mask] = sums[mask ^ low] + items[low.bit_length() - 1]
    return sums
