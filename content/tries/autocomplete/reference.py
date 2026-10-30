class Node:
    def __init__(self):
        self.children = {}
        self.end = False


def build(words):
    root = Node()
    for word in words:
        node = root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = Node()
            node = node.children[ch]
        node.end = True
    return root


def find(root, prefix):
    node = root
    for ch in prefix:
        node = node.children.get(ch)
        if node is None:
            return None
    return node


def collect(node, path, found):
    if node.end:
        found.append(path)
    for ch in sorted(node.children):
        if len(found) == 3:
            return
        collect(node.children[ch], path + ch, found)


def solve(words, queries):
    root = build(words)
    suggestions = []
    for query in queries:
        found = []
        node = find(root, query)
        if node is not None:
            collect(node, query, found)
        suggestions.append(found)
    return suggestions
