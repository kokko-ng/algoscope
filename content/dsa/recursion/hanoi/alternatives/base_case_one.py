# expect: fail
# Base case at count == 1 only: zero disks recurses forever.
def solve(disks):
    moves = []

    def move(count, source, target, spare):
        if count == 1:
            moves.append([source, target])
            return
        move(count - 1, source, spare, target)
        moves.append([source, target])
        move(count - 1, spare, target, source)

    move(disks, "A", "C", "B")
    return moves
