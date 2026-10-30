"""Helper types available to solutions: `from algoscope import ListNode, TreeNode`."""

from __future__ import annotations


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

    def __repr__(self):
        return f"ListNode({self.val!r})"


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

    def __repr__(self):
        return f"TreeNode({self.val!r})"


def build_list(values):
    """Build a singly linked list from a Python list and return its head."""
    head = None
    for v in reversed(list(values)):
        head = ListNode(v, head)
    return head


def list_values(head, limit=100_000):
    out = []
    while head is not None and len(out) < limit:
        out.append(head.val)
        head = head.next
    return out


def build_tree(values):
    """Build a binary tree from a level-order list where None marks a missing child."""
    values = list(values)
    if not values or values[0] is None:
        return None
    root = TreeNode(values[0])
    queue = [root]
    i = 1
    qi = 0
    while i < len(values) and qi < len(queue):
        node = queue[qi]
        qi += 1
        if i < len(values) and values[i] is not None:
            node.left = TreeNode(values[i])
            queue.append(node.left)
        i += 1
        if i < len(values) and values[i] is not None:
            node.right = TreeNode(values[i])
            queue.append(node.right)
        i += 1
    return root


def tree_values(root):
    """Level-order list with None for missing children, trailing Nones trimmed."""
    if root is None:
        return []
    out = []
    queue = [root]
    qi = 0
    while qi < len(queue):
        node = queue[qi]
        qi += 1
        if node is None:
            out.append(None)
            continue
        out.append(node.val)
        queue.append(node.left)
        queue.append(node.right)
    while out and out[-1] is None:
        out.pop()
    return out
