# expect: slow
# No trie: keep a list of words and compare every one on each query.
class Trie:
    def __init__(self):
        self.words = []

    def insert(self, word):
        self.words.append(word)

    def search(self, word):
        for w in self.words:
            if w == word:
                return True
        return False

    def starts_with(self, prefix):
        if prefix == "":
            return True
        for w in self.words:
            if w[: len(prefix)] == prefix:
                return True
        return False
