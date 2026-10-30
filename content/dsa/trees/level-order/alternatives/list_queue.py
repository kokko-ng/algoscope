# expect: slow
# Uses a plain list as the queue: pop(0) shifts every waiting node.
def solve(root):
    levels = []
    queue = [root] if root else []
    while queue:
        level = []
        for _ in range(len(queue)):
            node = queue.pop(0)
            level.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        levels.append(level)
    return levels
