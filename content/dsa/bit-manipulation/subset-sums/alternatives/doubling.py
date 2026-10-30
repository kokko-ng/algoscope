# expect: pass
# Each new item doubles the list: the old totals, then the old totals plus the item.
def solve(items):
    sums = [0]
    for item in items:
        sums += [total + item for total in sums]
    return sums
