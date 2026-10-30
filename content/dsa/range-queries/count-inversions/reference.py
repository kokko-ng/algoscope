def solve(nums):
    ranks = {value: r + 1 for r, value in enumerate(sorted(set(nums)))}
    tree = [0] * (len(ranks) + 1)
    inversions = 0
    for seen, value in enumerate(nums):
        i = ranks[value]
        at_most = 0
        while i > 0:
            at_most += tree[i]
            i -= i & -i
        inversions += seen - at_most
        i = ranks[value]
        while i < len(tree):
            tree[i] += 1
            i += i & -i
    return inversions
