class MinHeap:
    def __init__(self):
        self.items = []

    def push(self, value):
        self.items.append(value)
        child = len(self.items) - 1
        while child > 0:
            parent = (child - 1) // 2
            if self.items[parent] <= self.items[child]:
                break
            self.items[parent], self.items[child] = self.items[child], self.items[parent]
            child = parent

    def pop(self):
        top = self.items[0]
        last = self.items.pop()
        if self.items:
            self.items[0] = last
            self._sift_down(0)
        return top

    def _sift_down(self, parent):
        size = len(self.items)
        while True:
            smallest = parent
            left = 2 * parent + 1
            right = left + 1
            if left < size and self.items[left] < self.items[smallest]:
                smallest = left
            if right < size and self.items[right] < self.items[smallest]:
                smallest = right
            if smallest == parent:
                return
            self.items[parent], self.items[smallest] = self.items[smallest], self.items[parent]
            parent = smallest

    def peek(self):
        return self.items[0]

    def __len__(self):
        return len(self.items)
