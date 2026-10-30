from algoscope import TreeNode


def _bst(values):
    """Build a search tree by insertion. Returns (root, depth by value, parent by value)."""
    root = None
    depth, parent = {}, {}
    for value in values:
        if root is None:
            root = TreeNode(value)
            depth[value], parent[value] = 0, None
            continue
        node, d = root, 0
        while True:
            d += 1
            side = "left" if value < node.val else "right"
            child = getattr(node, side)
            if child is None:
                setattr(node, side, TreeNode(value))
                depth[value], parent[value] = d, node.val
                break
            node = child
    return root, depth, parent


def visual():
    root, _, _ = _bst([50, 30, 70, 20, 40, 60, 80, 35, 45, 33, 38])
    return (root, 33, 38)


def fixed():
    root, _, _ = _bst([8, 3, 10, 1, 6, 14, 4, 7, 13])
    single, _, _ = _bst([5])
    chain, _, _ = _bst([1, 2, 3, 4, 5])
    return [
        (single, 5, 5),
        (root, 1, 14),
        (root, 4, 7),
        (root, 7, 4),
        (root, 3, 7),
        (root, 13, 10),
        (root, 6, 6),
        (chain, 2, 5),
        (chain, 4, 5),
    ]


def cases(n, rng):
    n = max(n, 1)
    values = rng.sample(range(10 * n), n)
    root, _, _ = _bst(values)
    return [(root, rng.choice(values), rng.choice(values)) for _ in range(3)]


def bench(n, rng):
    values = rng.sample(range(10 * n), n)
    root, depth, parent = _bst(values)
    deep = sorted(values, key=lambda v: -depth[v])[: max(2, n // 10)]
    out = []
    for _ in range(20):
        p = rng.choice(deep)
        q = parent[p] if parent[p] is not None else p
        out.append((root, p, q) if rng.random() < 0.5 else (root, q, p))
    return out
