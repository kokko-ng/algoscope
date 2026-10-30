def visual():
    grid = [
        [1, 1, 5, 1],
        [3, 0, 5, 1],
        [1, 1, 9, 1],
        [4, 1, 1, 2],
    ]
    return (grid, (0, 0))


def cases(n, rng):
    side = max(2, int(n**0.5))
    grid = [[rng.randint(1, 9) for _ in range(side)] for _ in range(side)]
    return [(grid, (0, 0))]
