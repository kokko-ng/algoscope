# expect: fail
# Marks each node with an attribute, which the statement forbids (visit marks, modifying the list).
def solve(head):
    node = head
    while node is not None:
        if getattr(node, "seen", False):
            return node.val
        node.seen = True
        node = node.next
    return None
