# expect: fail
# Greedy: take the largest coin that fits, as many times as it fits.
def solve(coins, amount):
    count = 0
    left = amount
    for coin in sorted(coins, reverse=True):
        count += left // coin
        left %= coin
    return count if left == 0 else -1
