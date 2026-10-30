# expect: pass
# Literal reading: update the low before measuring, so each reading's own rise of 0 is a valid floor.
def solve(readings):
    low = float("inf")
    best = 0
    for x in readings:
        if x < low:
            low = x
        if x - low > best:
            best = x - low
    return best
