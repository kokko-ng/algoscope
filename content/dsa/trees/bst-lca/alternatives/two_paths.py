# expect: pass
# Walk to each value recording the path, then return the last node the two paths share.
def solve(root, p, q):
    def path(target):
        out = []
        node = root
        while node is not None:
            out.append(node.val)
            if target == node.val:
                break
            node = node.left if target < node.val else node.right
        return out

    a, b = path(p), path(q)
    answer = None
    for x, y in zip(a, b):
        if x != y:
            break
        answer = x
    return answer
