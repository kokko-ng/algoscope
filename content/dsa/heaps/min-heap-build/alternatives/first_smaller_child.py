# expect: fail
# Sift-down swaps with the first child that is smaller, not the smaller of the two children.
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
            parent = 0
            size = len(self.items)
            while True:
                left, right = 2 * parent + 1, 2 * parent + 2
                if left < size and self.items[left] < self.items[parent]:
                    nxt = left
                elif right < size and self.items[right] < self.items[parent]:
                    nxt = right
                else:
                    break
                self.items[parent], self.items[nxt] = self.items[nxt], self.items[parent]
                parent = nxt
        return top

    def peek(self):
        return self.items[0]

    def __len__(self):
        return len(self.items)
