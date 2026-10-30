# expect: fail
# insert sends equal values to the right instead of ignoring them, so duplicates appear in inorder().
from algoscope import TreeNode


class BST:
    def __init__(self):
        self.root = None

    def insert(self, value):
        if self.root is None:
            self.root = TreeNode(value)
            return
        node = self.root
        while True:
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

    def delete(self, value):
        self.root = self._delete(self.root, value)

    def _delete(self, node, value):
        if node is None:
            return None
        if value < node.val:
            node.left = self._delete(node.left, value)
        elif value > node.val:
            node.right = self._delete(node.right, value)
        elif node.left is None:
            return node.right
        elif node.right is None:
            return node.left
        else:
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
