# expect: slow
# A plain-list "heap": push appends, pop and peek scan every value for the minimum.
class MinHeap:
    def __init__(self):
        self.items = []

    def push(self, value):
        self.items.append(value)

    def _min_index(self):
        best = 0
        for i in range(1, len(self.items)):
            if self.items[i] < self.items[best]:
                best = i
        return best

    def pop(self):
        i = self._min_index()
        self.items[i], self.items[-1] = self.items[-1], self.items[i]
        return self.items.pop()

    def peek(self):
        return self.items[self._min_index()]

    def __len__(self):
        return len(self.items)
