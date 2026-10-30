from algoscope import TreeNode, build_tree


def _bst(values):
    root = None
    nodes = []
    for value in values:
        fresh = TreeNode(value)
        nodes.append(fresh)
        if root is None:
            root = fresh
            continue
        node = root
        while True:
            side = "left" if value < node.val else "right"
            child = getattr(node, side)
            if child is None:
                setattr(node, side, fresh)
                break
            node = child
    return root, nodes


def visual():
    return (build_tree([50, 30, 70, 20, 40, 45, 85]),)


def fixed():
    return [
        (None,),
        (build_tree([1]),),
        (build_tree([2, 1, 3]),),
        (build_tree([2, 3, 1]),),
        (build_tree([5, 3, 8, 1, 6]),),
        (build_tree([5, 3, 8, None, None, 4, 9]),),
        (build_tree([5, 5]),),
        (build_tree([5, None, 5]),),
        (build_tree([10, 5, 15, None, None, 12, 20]),),
        (build_tree([-3, -7, 0, None, -5]),),
    ]


def cases(n, rng):
    root, nodes = _bst(rng.sample(range(-5 * n - 10, 5 * n + 10), n))
    if n >= 2:
        r = rng.random()
        if r < 0.35:
            a, b = rng.sample(nodes, 2)
            a.val, b.val = b.val, a.val
        elif r < 0.5:
            parent = rng.choice([x for x in nodes if x.left or x.right] or nodes)
            child = parent.left or parent.right
            if child is not None:
                child.val = parent.val
    return [(root,)]


def bench(n, rng):
    root, _ = _bst(rng.sample(range(10 * n), n))
    return [(root,)]
