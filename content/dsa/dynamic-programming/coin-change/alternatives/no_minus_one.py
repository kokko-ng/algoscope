# expect: fail
# Forgets to turn the "unreachable" sentinel into -1.
def solve(coins, amount):
    fewest = [0] + [amount + 1] * amount
    for total in range(1, amount + 1):
        for coin in coins:
            if coin <= total and fewest[total - coin] + 1 < fewest[total]:
                fewest[total] = fewest[total - coin] + 1
    return fewest[amount]
