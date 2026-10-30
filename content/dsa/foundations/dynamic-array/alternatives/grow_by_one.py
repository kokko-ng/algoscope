# expect: slow
# Grow by one slot when full: correct, but n appends copy O(n^2) values.
class DynArray:
    def __init__(self):
        self.capacity = 0
        self.size = 0
        self.slots = [None] * 0

    def append(self, value):
        if self.size == self.capacity:
            bigger = [None] * (self.capacity + 1)
            for i in range(self.size):
                bigger[i] = self.slots[i]
            self.slots = bigger
            self.capacity += 1
        self.slots[self.size] = value
        self.size += 1

    def get(self, i):
        return self.slots[i]

    def set(self, i, value):
        self.slots[i] = value

    def pop(self):
        self.size -= 1
        return self.slots[self.size]

    def __len__(self):
        return self.size
