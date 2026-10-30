# expect: slow
# Splice each node of second into first by walking from the head every time: correct, but O(n * m).
from algoscope import ListNode


def solve(first, second):
    dummy = ListNode(None, first)
    while second is not None:
        node = second
        second = second.next
        prev = dummy
        while prev.next is not None and prev.next.val <= node.val:
            prev = prev.next
        node.next = prev.next
        prev.next = node
    return dummy.next
