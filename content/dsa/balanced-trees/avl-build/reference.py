from algoscope import TreeNode


def height_of(node):
    return node.height if node else 0


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
        return self._rebalance(node)

    def _rebalance(self, node):
        node.height = 1 + max(height_of(node.left), height_of(node.right))
        balance = height_of(node.left) - height_of(node.right)
        if balance > 1:
            if height_of(node.left.left) < height_of(node.left.right):
                node.left = self._rotate_left(node.left)
            return self._rotate_right(node)
        if balance < -1:
            if height_of(node.right.right) < height_of(node.right.left):
                node.right = self._rotate_right(node.right)
            return self._rotate_left(node)
        return node

    def _rotate_left(self, node):
        pivot = node.right
        node.right = pivot.left
        pivot.left = node
        node.height = 1 + max(height_of(node.left), height_of(node.right))
        pivot.height = 1 + max(height_of(pivot.left), height_of(pivot.right))
        return pivot

    def _rotate_right(self, node):
        pivot = node.left
        node.left = pivot.right
        pivot.right = node
        node.height = 1 + max(height_of(node.left), height_of(node.right))
        pivot.height = 1 + max(height_of(pivot.left), height_of(pivot.right))
        return pivot

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
        return height_of(self.root)
