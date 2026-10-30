class RingQueue:
    def __init__(self, capacity=4):
        self.slots = [None] * capacity
        self.front = 0
        self.size = 0

    def _grow(self):
        bigger = [None] * (2 * len(self.slots))
        for i in range(self.size):
            bigger[i] = self.slots[(self.front + i) % len(self.slots)]
        self.slots = bigger
        self.front = 0

    def enqueue(self, value):
        if self.size == len(self.slots):
            self._grow()
        back = (self.front + self.size) % len(self.slots)
        self.slots[back] = value
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
        if self.size == 0:
            return None
        return self.slots[self.front]

    def __len__(self):
        return self.size
