# expect: pass
# Recursive sift-up and sift-down instead of loops.
class MinHeap:
    def __init__(self):
        self.items = []

    def push(self, value):
        self.items.append(value)
        self._up(len(self.items) - 1)

    def _up(self, i):
        parent = (i - 1) // 2
        if i > 0 and self.items[i] < self.items[parent]:
            self.items[i], self.items[parent] = self.items[parent], self.items[i]
            self._up(parent)

    def _down(self, i):
        smallest = i
        for child in (2 * i + 1, 2 * i + 2):
            if child < len(self.items) and self.items[child] < self.items[smallest]:
                smallest = child
        if smallest != i:
            self.items[i], self.items[smallest] = self.items[smallest], self.items[i]
            self._down(smallest)

    def pop(self):
        self.items[0], self.items[-1] = self.items[-1], self.items[0]
        top = self.items.pop()
        if self.items:
            self._down(0)
        return top

    def peek(self):
        return self.items[0]

    def __len__(self):
        return len(self.items)
