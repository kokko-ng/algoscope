# expect: pass
# No placeholder: pick the head explicitly, then relink the rest.
def solve(first, second):
    if first is None:
        return second
    if second is None:
        return first
    if second.val < first.val:
        first, second = second, first
    head = tail = first
    first = first.next
    while first is not None and second is not None:
        if first.val <= second.val:
            tail.next, first = first, first.next
        else:
            tail.next, second = second, second.next
        tail = tail.next
    tail.next = first if first is not None else second
    return head
