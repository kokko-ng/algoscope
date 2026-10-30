# expect: silver
# Top-down recursion with a memo dict: the same O(nk) states as the table, about twice the steps.
def solve(coins, amount):
    memo = {0: 0}

    def fewest(total):
        if total in memo:
            return memo[total]
        best = -1
        for coin in coins:
            if coin <= total:
                sub = fewest(total - coin)
                if sub >= 0 and (best < 0 or sub + 1 < best):
                    best = sub + 1
        memo[total] = best
        return best

    return fewest(amount)
