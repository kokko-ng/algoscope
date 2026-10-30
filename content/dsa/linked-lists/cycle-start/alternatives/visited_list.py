# expect: slow
# Remember visited nodes in a Python list and scan it for each new node: correct, but O(n^2).
def solve(head):
    visited = []
    node = head
    while node is not None:
        for seen in visited:
            if seen is node:
                return node.val
        visited += [node]
        node = node.next
    return None
