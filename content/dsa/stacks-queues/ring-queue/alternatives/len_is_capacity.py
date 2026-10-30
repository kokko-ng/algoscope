# expect: fail
# __len__ reports the number of slots instead of the number of stored values.
class RingQueue:
    def __init__(self, capacity=4):
        self.slots = [None] * capacity
        self.front = 0
        self.size = 0

    def enqueue(self, value):
        if self.size == len(self.slots):
            bigger = [None] * (2 * len(self.slots))
            for i in range(self.size):
                bigger[i] = self.slots[(self.front + i) % len(self.slots)]
            self.slots = bigger
            self.front = 0
        self.slots[(self.front + self.size) % len(self.slots)] = value
        self.size += 1

    def dequeue(self):
        if self.size == 0:
            return None
        value = self.slots[self.front]
        self.front = (self.front + 1) % len(self.slots)
        self.size -= 1
        return value

    def peek(self):
        return self.slots[self.front] if self.size else None

    def __len__(self):
        return len(self.slots)
