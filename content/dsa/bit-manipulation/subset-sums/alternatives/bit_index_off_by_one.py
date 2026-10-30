# expect: fail
# Uses bit_length() as the index: one position too far.
def solve(items):
    sums = [0] * (1 << len(items))
    for mask in range(1, len(sums)):
        low = mask & -mask
        index = low.bit_length()
        sums[mask] = sums[mask ^ low] + (items[index] if index < len(items) else 0)
    return sums
