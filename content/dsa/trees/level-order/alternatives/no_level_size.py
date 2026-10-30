# expect: fail
# Drains the queue without fixing the level size first, so every level merges into one list.
from collections import deque


def solve(root):
    levels = []
    queue = deque([root] if root else [])
    while queue:
        level = []
        while queue:
            node = queue.popleft()
            level.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        levels.append(level)
    return levels
