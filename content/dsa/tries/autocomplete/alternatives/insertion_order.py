# expect: fail
# Explores children in insertion order rather than alphabetical order.
class Node:
    def __init__(self):
        self.children = {}
        self.end = False


def solve(words, queries):
    root = Node()
    for word in words:
        node = root
        for ch in word:
            node = node.children.setdefault(ch, Node())
        node.end = True

    def collect(node, path, found):
        if node.end:
            found.append(path)
        for ch in node.children:
            if len(found) == 3:
                return
            collect(node.children[ch], path + ch, found)

    out = []
    for q in queries:
        node = root
        for ch in q:
            node = node.children.get(ch)
            if node is None:
                break
        found = []
        if node is not None:
            collect(node, q, found)
        out.append(found)
    return out
