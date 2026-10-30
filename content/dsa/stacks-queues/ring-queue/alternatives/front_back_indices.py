# expect: pass
# Tracks both a front and a back index plus a count, and enqueue returns the new length.
class RingQueue:
    def __init__(self, capacity=4):
        self.slots = [None] * capacity
        self.head = 0
        self.tail = 0
        self.count = 0

    def enqueue(self, value):
        if self.count == len(self.slots):
            old = self.slots
            self.slots = [None] * (2 * len(old))
            for i in range(self.count):
                self.slots[i] = old[(self.head + i) % len(old)]
            self.head = 0
            self.tail = self.count
        self.slots[self.tail] = value
        self.tail = (self.tail + 1) % len(self.slots)
        self.count += 1
        return self.count

    def dequeue(self):
        if self.count == 0:
            return None
        value = self.slots[self.head]
        self.head = (self.head + 1) % len(self.slots)
        self.count -= 1
        return value

    def peek(self):
        if self.count == 0:
            return None
        return self.slots[self.head]

    def __len__(self):
        return self.count
