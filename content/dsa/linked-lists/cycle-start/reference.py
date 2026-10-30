def solve(head):
    slow = fast = head
    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            break
    else:
        return None
    seeker = head
    while seeker is not slow:
        seeker = seeker.next
        slow = slow.next
    return seeker.val
