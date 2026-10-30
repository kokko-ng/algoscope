class Node:
    def __init__(self):
        self.children = {}
        self.end = False


def solve(words, queries):
    root = Node()
    for word in words:
        node = root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = Node()
            node = node.children[ch]
        node.end = True

    def collect(node, path, found):
        if node.end:
            found.append(path)
        for ch in sorted(node.children):
            if len(found) == 3:
                return
            collect(node.children[ch], path + ch, found)

    suggestions = []
    for query in queries:
        node = root
        for ch in query:
            node = node.children.get(ch)
            if node is None:
                break
        found = []
        if node is not None:
            collect(node, query, found)
        suggestions.append(found)
    return suggestions
