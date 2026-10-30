# expect: slow
# Count the nodes, then walk again to the one before the target: correct, but two passes.
def solve(head, k):
    length = 0
    node = head
    while node is not None:
        length += 1
        node = node.next
    if k == length:
        return head.next
    prev = head
    for _ in range(length - k - 1):
        prev = prev.next
    prev.next = prev.next.next
    return head
