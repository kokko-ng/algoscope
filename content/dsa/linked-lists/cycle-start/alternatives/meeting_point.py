# expect: fail
# Returns where the slow and fast pointers meet, which is inside the loop but not its first node.
def solve(head):
    slow = fast = head
    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            return slow.val
    return None
