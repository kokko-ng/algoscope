# expect: slow
# Keeps the front at slot 0 and shifts every value left on dequeue: O(n) per dequeue.
class RingQueue:
    def __init__(self, capacity=4):
        self.slots = [None] * capacity
        self.size = 0

    def enqueue(self, value):
        if self.size == len(self.slots):
            bigger = [None] * (2 * len(self.slots))
            for i in range(self.size):
                bigger[i] = self.slots[i]
            self.slots = bigger
        self.slots[self.size] = value
        self.size += 1

    def dequeue(self):
        if self.size == 0:
            return None
        value = self.slots[0]
        for i in range(1, self.size):
            self.slots[i - 1] = self.slots[i]
        self.size -= 1
        self.slots[self.size] = None
        return value

    def peek(self):
        return self.slots[0] if self.size else None

    def __len__(self):
        return self.size
