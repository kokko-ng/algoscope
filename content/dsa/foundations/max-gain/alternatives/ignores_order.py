# expect: fail
# max - min ignores that the low reading must come first.
def solve(readings):
    if not readings:
        return 0
    return max(readings) - min(readings)
