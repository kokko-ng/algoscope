# expect: pass
# Each trie node stores its first three words in order, updated on insert; a query just reads it.
class Node:
    def __init__(self):
        self.children = {}
        self.top = []


def solve(words, queries):
    root = Node()
    for word in words:
        path = [root]
        for ch in word:
            path.append(path[-1].children.setdefault(ch, Node()))
        for node in path:
            if word in node.top:
                continue
            node.top.append(word)
            i = len(node.top) - 1
            while i > 0 and node.top[i - 1] > node.top[i]:
                node.top[i - 1], node.top[i] = node.top[i], node.top[i - 1]
                i -= 1
            if len(node.top) > 3:
                node.top.pop()
    out = []
    for q in queries:
        node = root
        for ch in q:
            node = node.children.get(ch)
            if node is None:
                break
        out.append(list(node.top) if node else [])
    return out
