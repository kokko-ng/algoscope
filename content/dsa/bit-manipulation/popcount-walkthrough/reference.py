def solve(n):
    count = 0
    while n:
        below = n - 1
        n = n & below
        count += 1
    return count
