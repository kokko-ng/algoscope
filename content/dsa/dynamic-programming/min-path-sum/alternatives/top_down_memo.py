# expect: pass
# Top-down recursion with a memo dict instead of a bottom-up table.
def solve(grid):
    memo = {}

    def cheapest(r, c):
        if (r, c) in memo:
            return memo[(r, c)]
        if r == 0 and c == 0:
            best = 0
        elif r == 0:
            best = cheapest(r, c - 1)
        elif c == 0:
            best = cheapest(r - 1, c)
        else:
            best = min(cheapest(r - 1, c), cheapest(r, c - 1))
        memo[(r, c)] = best + grid[r][c]
        return memo[(r, c)]

    return cheapest(len(grid) - 1, len(grid[0]) - 1)
