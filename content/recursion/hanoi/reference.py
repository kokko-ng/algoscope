def solve(disks):
    pegs = {"A": list(range(disks, 0, -1)), "B": [], "C": []}
    moves = []

    def move(count, source, target, spare):
        if count == 0:
            return
        move(count - 1, source, spare, target)
        pegs[target].append(pegs[source].pop())
        moves.append([source, target])
        move(count - 1, spare, target, source)

    move(disks, "A", "C", "B")
    return moves
