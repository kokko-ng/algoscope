# expect: fail
# Never counts words at the root, so the empty prefix gives 0.
class Node:
    def __init__(self):
        self.children = {}
        self.count = 0


def solve(words, prefixes):
    root = Node()
    for word in words:
        node = root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = Node()
            node = node.children[ch]
            node.count += 1
    counts = []
    for prefix in prefixes:
        node = root
        for ch in prefix:
            node = node.children.get(ch)
            if node is None:
                break
        counts.append(node.count if node else 0)
    return counts
