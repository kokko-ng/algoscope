# expect: slow
# Follows the rule literally: try bits from the lowest and remember used codes in a set.
def solve(n):
    codes = [0]
    used = {0}
    while len(codes) < 1 << n:
        for bit in range(n):
            nxt = codes[-1] ^ (1 << bit)
            if nxt not in used:
                break
        codes.append(nxt)
        used.add(nxt)
    return codes
