from algoscope import TreeNode, build_tree


def _random_tree(n, rng):
    """A random shape: each new node hangs off a random free child slot."""
    if n == 0:
        return None
    root = TreeNode(rng.randint(0, 99))
    slots = [(root, "left"), (root, "right")]
    for _ in range(n - 1):
        parent, side = slots.pop(rng.randrange(len(slots)))
        child = TreeNode(rng.randint(0, 99))
        setattr(parent, side, child)
        slots.append((child, "left"))
        slots.append((child, "right"))
    return root


def visual():
    return (build_tree([3, 9, 20, None, 4, 15, 7, None, None, 8]),)


def fixed():
    return [
        (None,),
        (build_tree([1]),),
        (build_tree([1, 2]),),
        (build_tree([1, None, 2, None, 3]),),
        (build_tree([1, 2, 3, 4, 5, 6, 7]),),
    ]


def cases(n, rng):
    return [(_random_tree(n, rng),)]
