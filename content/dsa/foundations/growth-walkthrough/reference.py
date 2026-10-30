class DynArray:
    def __init__(self):
        self.capacity = 1
        self.size = 0
        self.slots = [None] * self.capacity

    def append(self, value):
        if self.size < self.capacity:
            self.slots[self.size] = value
            self.size += 1
            return
        bigger = [None] * (self.capacity * 2)
        for i in range(self.size):
            bigger[i] = self.slots[i]
        self.slots = bigger
        self.capacity *= 2
        self.append(value)
