from algoscope import ListNode


def solve(head, k):
    dummy = ListNode(0, head)
    lead = trail = dummy
    for _ in range(k):
        lead = lead.next
    while lead.next is not None:
        lead = lead.next
        trail = trail.next
    trail.next = trail.next.next
    return dummy.next
