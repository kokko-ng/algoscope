class TrieNode:
    def __init__(self):
        self.children = {}
        self.end = False


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        pass

    def search(self, word):
        # True only if word itself was inserted
        pass

    def starts_with(self, prefix):
        # True if any inserted word begins with prefix
        pass
