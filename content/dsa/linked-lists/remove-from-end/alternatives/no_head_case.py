# expect: fail
# No placeholder in front of head, so removing the head itself (k == length) crashes.
def solve(head, k):
    lead = trail = head
    for _ in range(k):
        lead = lead.next
    while lead.next is not None:
        lead = lead.next
        trail = trail.next
    trail.next = trail.next.next
    return head
