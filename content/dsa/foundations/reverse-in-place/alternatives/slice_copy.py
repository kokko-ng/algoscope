# expect: fail
# Builds a second list with a slice and copies it back, which the statement forbids.
def solve(items):
    items[:] = items[::-1]
