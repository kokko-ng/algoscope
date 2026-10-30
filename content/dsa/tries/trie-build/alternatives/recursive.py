# expect: pass
# Recursive insert and walk, one character per call.
class TrieNode:
    def __init__(self):
        self.children = {}
        self.end = False


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        def put(node, i):
            if i == len(word):
                node.end = True
                return
            child = node.children.setdefault(word[i], TrieNode())
            put(child, i + 1)

        put(self.root, 0)

    def _walk(self, node, text, i):
        if node is None or i == len(text):
            return node
        return self._walk(node.children.get(text[i]), text, i + 1)

    def search(self, word):
        node = self._walk(self.root, word, 0)
        return bool(node and node.end)

    def starts_with(self, prefix):
        return self._walk(self.root, prefix, 0) is not None
