# expect: slow
# Naive table: a total is one coin, or the best split into two smaller totals. O(n^2) in the amount.
def solve(coins, amount):
    inf = float("inf")
    fewest = [inf] * (amount + 1)
    fewest[0] = 0
    for total in range(1, amount + 1):
        if total in coins:
            fewest[total] = 1
            continue
        for part in range(1, total // 2 + 1):
            if fewest[part] + fewest[total - part] < fewest[total]:
                fewest[total] = fewest[part] + fewest[total - part]
    return fewest[amount] if fewest[amount] != inf else -1
