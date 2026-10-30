# expect: pass
# Recursive insert, contains and inorder instead of loops.
from algoscope import TreeNode


class BST:
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
        return node

    def contains(self, value):
        return self._contains(self.root, value)

    def _contains(self, node, value):
        if node is None:
            return False
        if value == node.val:
            return True
        return self._contains(node.left if value < node.val else node.right, value)

    def delete(self, value):
        self.root = self._delete(self.root, value)

    def _delete(self, node, value):
        if node is None:
            return None
        if value < node.val:
            node.left = self._delete(node.left, value)
            return node
        if value > node.val:
            node.right = self._delete(node.right, value)
            return node
        if node.left is None:
            return node.right
        if node.right is None:
            return node.left
        successor = node.right
        while successor.left is not None:
            successor = successor.left
        node.val = successor.val
        node.right = self._delete(node.right, successor.val)
        return node

    def inorder(self):
        values = []

        def walk(node):
            if node:
                walk(node.left)
                values.append(node.val)
                walk(node.right)

        walk(self.root)
        return values
