# expect: pass
# Measure the loop length after the pointers meet, then walk two pointers that far apart.
def solve(head):
    slow = fast = head
    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            break
    else:
        return None
    length = 1
    probe = slow.next
    while probe is not slow:
        probe = probe.next
        length += 1
    ahead = behind = head
    for _ in range(length):
        ahead = ahead.next
    while ahead is not behind:
        ahead = ahead.next
        behind = behind.next
    return behind.val
