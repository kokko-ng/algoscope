# expect: slow
# Correct rotations, but heights are recomputed by walking whole subtrees instead of stored on nodes.
from algoscope import TreeNode


def height_of(node):
    if node is None:
        return 0
    return 1 + max(height_of(node.left), height_of(node.right))


def rotate_left(node):
    pivot = node.right
    node.right = pivot.left
    pivot.left = node
    return pivot


def rotate_right(node):
    pivot = node.left
    node.left = pivot.right
    pivot.right = node
    return pivot


class AVL:
    def __init__(self):
        self.root = None

    def insert(self, value):
        self.root = self._insert(self.root, value)

    def _insert(self, node, value):
        if node is None:
            return TreeNode(value)
        if value < node.val:
            node.left = self._insert(node.left, value)
        elif value > node.val:
            node.right = self._insert(node.right, value)
        else:
            return node
        balance = height_of(node.left) - height_of(node.right)
        if balance > 1:
            if height_of(node.left.left) < height_of(node.left.right):
                node.left = rotate_left(node.left)
            return rotate_right(node)
        if balance < -1:
            if height_of(node.right.right) < height_of(node.right.left):
                node.right = rotate_right(node.right)
            return rotate_left(node)
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
