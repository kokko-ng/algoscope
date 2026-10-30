# expect: fail
# Returns the placeholder node itself, so the result starts with an extra 0.
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
    tail.next = first if first is not None else second
    return dummy
