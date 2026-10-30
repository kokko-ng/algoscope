# expect: fail
# Stops only where the trie branches, walking past a node where a shorter word ends.
class Node:
    def __init__(self):
        self.children = {}
        self.end = False


def solve(words):
    if not words:
        return ""
    root = Node()
    for word in words:
        node = root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = Node()
            node = node.children[ch]
        node.end = True
    prefix = []
    node = root
    while len(node.children) == 1:
        ch, node = next(iter(node.children.items()))
        prefix.append(ch)
    return "".join(prefix)
