# expect: pass
# Recursive pre-order walk that files each value under its depth; left-before-right keeps each level in order.
def solve(root):
    levels = []

    def walk(node, depth):
        if node is None:
            return
        if depth == len(levels):
            levels.append([])
        levels[depth].append(node.val)
        walk(node.left, depth + 1)
        walk(node.right, depth + 1)

    walk(root, 0)
    return levels
