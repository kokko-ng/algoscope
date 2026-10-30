# expect: fail
# Grows by copying slots in storage order and resetting front, which scrambles a wrapped queue.
class RingQueue:
    def __init__(self, capacity=4):
        self.slots = [None] * capacity
        self.front = 0
        self.size = 0

    def enqueue(self, value):
        if self.size == len(self.slots):
            bigger = [None] * (2 * len(self.slots))
            for i in range(len(self.slots)):
                bigger[i] = self.slots[i]
            self.slots = bigger
            self.front = 0
        self.slots[(self.front + self.size) % len(self.slots)] = value
        self.size += 1

    def dequeue(self):
        if self.size == 0:
            return None
        value = self.slots[self.front]
        self.slots[self.front] = None
        self.front = (self.front + 1) % len(self.slots)
        self.size -= 1
        return value

    def peek(self):
        return self.slots[self.front] if self.size else None

    def __len__(self):
        return self.size
