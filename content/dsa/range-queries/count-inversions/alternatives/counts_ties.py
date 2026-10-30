# expect: fail
# Queries one rank too low, so earlier equal values are counted as larger.
def solve(nums):
    ranks = {value: r + 1 for r, value in enumerate(sorted(set(nums)))}
    tree = [0] * (len(ranks) + 1)
    inversions = 0
    for seen, value in enumerate(nums):
        i = ranks[value] - 1
        smaller = 0
        while i > 0:
            smaller += tree[i]
            i -= i & -i
        inversions += seen - smaller
        i = ranks[value]
        while i < len(tree):
            tree[i] += 1
            i += i & -i
    return inversions
