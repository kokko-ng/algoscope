# expect: fail
# Stops when either list runs out and forgets to attach the rest of the other.
from algoscope import ListNode


def solve(first, second):
    dummy = ListNode()
    tail = dummy
    while first is not None and second is not None:
        if first.val <= second.val:
            tail.next = first
            first = first.next
        else:
            tail.next = second
            second = second.next
        tail = tail.next
    tail.next = None
    return dummy.next
