"""Helper types available to solutions: `from algoscope import ListNode, TreeNode`."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Iterable


class ListNode:
    """A singly linked list node."""

    # `next` is the conventional field name for a linked list node
    def __init__(self, val: Any = 0, next: ListNode | None = None) -> None:  # noqa: A002
        """Create a node holding `val` that links to `next`."""
        self.val = val
        self.next = next

    def __repr__(self) -> str:
        """Show the node by its value."""
        return f"ListNode({self.val!r})"


class TreeNode:
    """A binary tree node."""

    def __init__(self, val: Any = 0, left: TreeNode | None = None, right: TreeNode | None = None) -> None:
        """Create a node holding `val` with optional children."""
        self.val = val
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        """Show the node by its value."""
        return f"TreeNode({self.val!r})"


def build_list(values: Iterable[Any]) -> ListNode | None:
    """Build a singly linked list from a Python list and return its head."""
    head: ListNode | None = None
    for v in reversed(list(values)):
        head = ListNode(v, head)
    return head


def list_values(head: ListNode | None, limit: int = 100_000) -> list[Any]:
    """Values of a linked list from the head, stopping after `limit` nodes."""
    out: list[Any] = []
    while head is not None and len(out) < limit:
        out.append(head.val)
        head = head.next
    return out


def build_tree(values: Iterable[Any]) -> TreeNode | None:
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


def tree_values(root: TreeNode | None) -> list[Any]:
    """Level-order list with None for missing children, trailing Nones trimmed."""
    if root is None:
        return []
    out: list[Any] = []
    queue: list[TreeNode | None] = [root]
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
