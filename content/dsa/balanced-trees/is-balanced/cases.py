from algoscope import TreeNode, build_tree


def _middle(lo, hi):
    if lo > hi:
        return None
    mid = (lo + hi) // 2
    return TreeNode(mid, _middle(lo, mid - 1), _middle(mid + 1, hi))


def _h(node):
    return node.height if node else 0


def _fix(node):
    node.height = 1 + max(_h(node.left), _h(node.right))


def _rot(node, side):
    other = "right" if side == "left" else "left"
    pivot = getattr(node, other)
    setattr(node, other, getattr(pivot, side))
    setattr(pivot, side, node)
    _fix(node)
    _fix(pivot)
    return pivot


def _avl_insert(node, value):
    if node is None:
        leaf = TreeNode(value)
        leaf.height = 1
        return leaf
    if value < node.val:
        node.left = _avl_insert(node.left, value)
    else:
        node.right = _avl_insert(node.right, value)
    _fix(node)
    balance = _h(node.left) - _h(node.right)
    if balance > 1:
        if _h(node.left.left) < _h(node.left.right):
            node.left = _rot(node.left, "left")
        return _rot(node, "right")
    if balance < -1:
        if _h(node.right.right) < _h(node.right.left):
            node.right = _rot(node.right, "right")
        return _rot(node, "left")
    return node


def _avl(values):
    root = None
    for value in values:
        root = _avl_insert(root, value)
    return root


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


def _graft(root, length, rng):
    """Hang a chain of `length` nodes below a random leaf."""
    node = root
    while node.left or node.right:
        choices = [c for c in (node.left, node.right) if c]
        node = rng.choice(choices)
    for k in range(length):
        child = TreeNode(-1 - k)
        if rng.random() < 0.5:
            node.left = child
        else:
            node.right = child
        node = child
    return root


def visual():
    return (build_tree([1, 2, 3, 4, None, None, 5, 6]),)


def fixed():
    return [
        (None,),
        (TreeNode(1),),
        (build_tree([1, 2]),),
        (build_tree([1, 2, None, 3]),),
        (build_tree([1, 2, 3, 4, None, None, 5, 6, None, None, 7]),),
        (build_tree([1, 2, 3, 4, 5, 6, None, 8]),),
        (build_tree([1, 2, 3, 4, 5, None, None, 8, 9]),),
        (build_tree([1, None, 2, None, 3]),),
    ]


def cases(n, rng):
    if n == 0:
        return [(None,)]
    kind = rng.randrange(4)
    values = rng.sample(range(5 * n + 5), n)
    if kind == 0:
        root = _middle(1, n)
    elif kind == 1:
        root = _avl(values)
    elif kind == 2:
        root = _bst(values)
    else:
        root = _graft(_avl(values), 2, rng)
    return [(root,)]


def bench(n, rng):
    return [(_middle(1, n),)]
