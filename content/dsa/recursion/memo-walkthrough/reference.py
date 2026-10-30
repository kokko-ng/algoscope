def solve(n):
    memo = {}

    def fib(k):
        if k < 2:
            return k
        if k not in memo:
            memo[k] = fib(k - 1) + fib(k - 2)
        return memo[k]

    return fib(n)
