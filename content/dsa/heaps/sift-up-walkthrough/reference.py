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
