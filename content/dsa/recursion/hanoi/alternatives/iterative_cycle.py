# expect: pass
# Iterative: alternate moving the smallest disk around a fixed cycle with the only other legal move.
def solve(disks):
    pegs = {"A": list(range(disks, 0, -1)), "B": [], "C": []}
    order = ["A", "B", "C"] if disks % 2 == 0 else ["A", "C", "B"]
    moves = []
    at = 0
    for step in range(2**disks - 1):
        if step % 2 == 0:
            src, dst = order[at], order[(at + 1) % 3]
            at = (at + 1) % 3
        else:
            x, y = [p for p in "ABC" if p != order[at]]
            if not pegs[x] or (pegs[y] and pegs[y][-1] < pegs[x][-1]):
                x, y = y, x
            src, dst = x, y
        pegs[dst].append(pegs[src].pop())
        moves.append([src, dst])
    return moves
