# expect: slow
# Returns new move lists and glues them with +, copying every list again at each level.
def solve(disks):
    def move(count, source, target, spare):
        if count == 0:
            return []
        return move(count - 1, source, spare, target) + [[source, target]] + move(count - 1, spare, target, source)

    return move(disks, "A", "C", "B")
