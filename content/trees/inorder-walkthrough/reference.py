def solve(root):
    visited = []

    def walk(node):
        if node is None:
            return
        walk(node.left)
        visited.append(node.val)
        walk(node.right)

    walk(root)
    return visited
