from algoscope import TreeNode, build_tree


def visual():
    return (build_tree([50, 30, 70, 20, 40, None, 85, None, None, 35]),)


def _bst(values):
    root = None
    for value in values:
        if root is None:
            root = TreeNode(value)
            continue
        node = root
        while True:
            side = "left" if value < node.val else "right"
            child = getattr(node, side)
            if child is None:
                setattr(node, side, TreeNode(value))
                break
            node = child
    return root


def cases(n, rng):
    return [(_bst(rng.sample(range(10 * n + 10), n)),)]
