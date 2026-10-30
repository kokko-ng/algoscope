# expect: fail
# Always rotates once at the lopsided node. A zig-zag (inside grandchild) stays lopsided.
from algoscope import TreeNode


def height_of(node):
    return node.height if node else 0


def fix(node):
    node.height = 1 + max(height_of(node.left), height_of(node.right))


class AVL:
    def __init__(self):
        self.root = None

    def insert(self, value):
        self.root = self._insert(self.root, value)

    def _insert(self, node, value):
        if node is None:
            leaf = TreeNode(value)
            leaf.height = 1
            return leaf
        if value < node.val:
            node.left = self._insert(node.left, value)
        elif value > node.val:
            node.right = self._insert(node.right, value)
        else:
            return node
        fix(node)
        balance = height_of(node.left) - height_of(node.right)
        if balance > 1:
            pivot = node.left
            node.left = pivot.right
            pivot.right = node
            fix(node)
            fix(pivot)
            return pivot
        if balance < -1:
            pivot = node.right
            node.right = pivot.left
            pivot.left = node
            fix(node)
            fix(pivot)
            return pivot
        return node

    def contains(self, value):
        node = self.root
        while node is not None:
            if value == node.val:
                return True
            node = node.left if value < node.val else node.right
        return False

    def inorder(self):
        out = []

        def walk(node):
            if node:
                walk(node.left)
                out.append(node.val)
                walk(node.right)

        walk(self.root)
        return out

    def height(self):
        return height_of(self.root)
