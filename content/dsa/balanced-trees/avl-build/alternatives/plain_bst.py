# expect: fail
# A plain search tree with no rotations: correct order, but height() reports a chain, not an AVL tree.
from algoscope import TreeNode


class AVL:
    def __init__(self):
        self.root = None

    def insert(self, value):
        if self.root is None:
            self.root = TreeNode(value)
            return
        node = self.root
        while value != node.val:
            side = "left" if value < node.val else "right"
            child = getattr(node, side)
            if child is None:
                setattr(node, side, TreeNode(value))
                return
            node = child

    def contains(self, value):
        node = self.root
        while node is not None:
            if value == node.val:
                return True
            node = node.left if value < node.val else node.right
        return False

    def inorder(self):
        values = []
        stack = []
        node = self.root
        while stack or node is not None:
            while node is not None:
                stack.append(node)
                node = node.left
            node = stack.pop()
            values.append(node.val)
            node = node.right
        return values

    def height(self):
        best = 0
        stack = [(self.root, 1)] if self.root else []
        while stack:
            node, depth = stack.pop()
            best = max(best, depth)
            for child in (node.left, node.right):
                if child is not None:
                    stack.append((child, depth + 1))
        return best
