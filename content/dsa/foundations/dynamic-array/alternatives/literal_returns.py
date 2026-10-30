# expect: pass
# Literal reading: start with 4 slots, set returns the value, pop leaves the old slot in place.
class DynArray:
    def __init__(self):
        self.slots = [None] * 4
        self.n = 0

    def append(self, value):
        if self.n == len(self.slots):
            old = self.slots
            self.slots = [None] * (2 * len(old))
            for i in range(self.n):
                self.slots[i] = old[i]
        self.slots[self.n] = value
        self.n += 1

    def get(self, i):
        return self.slots[i]

    def set(self, i, value):
        self.slots[i] = value
        return value

    def pop(self):
        self.n -= 1
        return self.slots[self.n]

    def __len__(self):
        return self.n
