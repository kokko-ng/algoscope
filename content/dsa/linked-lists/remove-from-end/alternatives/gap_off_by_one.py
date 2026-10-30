# expect: fail
# Off-by-one gap: starts the lead k - 1 nodes ahead, so it targets the (k - 1)-th node from the end.
from algoscope import ListNode


def solve(head, k):
    dummy = ListNode(0, head)
    lead = trail = dummy
    for _ in range(k - 1):
        lead = lead.next
    while lead.next is not None:
        lead = lead.next
        trail = trail.next
    trail.next = trail.next.next
    return dummy.next
