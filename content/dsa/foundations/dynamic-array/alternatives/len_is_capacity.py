# expect: fail
# __len__ reports the allocated capacity instead of the number of stored values.
class DynArray:
    def __init__(self):
        self.capacity = 1
        self.size = 0
        self.slots = [None] * self.capacity

    def append(self, value):
        if self.size == self.capacity:
            bigger = [None] * (self.capacity * 2)
            for i in range(self.size):
                bigger[i] = self.slots[i]
            self.slots = bigger
            self.capacity *= 2
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
        return self.capacity
